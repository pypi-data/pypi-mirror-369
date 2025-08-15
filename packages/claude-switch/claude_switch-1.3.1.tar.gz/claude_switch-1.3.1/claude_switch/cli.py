import sys
import os
import click
import questionary
from pathlib import Path
from typing import Optional, List, Dict, Any
from .config import ConfigManager


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='显示版本信息')
@click.option('--no-auto-init', is_flag=True, help='禁用自动初始化')
@click.pass_context
def cli(ctx, version, no_auto_init):
    """Claude Switch - Anthropic Claude API 配置管理工具，支持多环境切换"""
    if version:
        click.echo("claude-switch 1.2.0")
        click.echo("Anthropic Claude API 配置管理工具")
        click.echo("GitHub: https://github.com/elicc/claude-switch")
        return

    # 检查是否需要自动初始化
    if not no_auto_init and ctx.invoked_subcommand is None:
        cm = ConfigManager()
        if not cm.is_initialized():
            click.echo("🔧 首次使用，正在初始化 Claude Switch...")
            click.echo("")

            # 自动执行初始化
            result = cm.init_shell()
            click.echo(result)
            click.echo("")

            # 检查是否需要添加配置
            configs = cm.get_configs()
            if not configs or len(configs) == 0:
                click.echo("🎯 检测到尚无配置，建议立即添加一个配置：")
                if click.confirm("是否现在添加第一个配置？", default=True):
                    add_first_config_interactive(cm)
                    # 如果添加了配置，直接进入选择界面
                    click.echo("")
                    interactive_select()
                    return
            else:
                click.echo(f"📋 当前已有 {len(configs)} 个配置")
                click.echo("")
                # 直接进入选择界面
                interactive_select()
                return

    if ctx.invoked_subcommand is None:
        interactive_select()


@cli.command()
def list():
    """列出所有配置"""
    cm = ConfigManager()
    configs = cm.get_configs()
    current = cm.get_current_config_name()

    if not configs:
        click.echo("暂无配置")
        return

    for name, config in configs.items():
        prefix = "→ " if name == current else "  "
        display = format_config_display(name, config)
        # 为当前激活的配置添加背景色高亮
        if name == current:
            # 使用 ANSI 颜色码添加绿色背景
            click.echo(f"\033[42m\033[30m{prefix}{display}\033[0m")
        else:
            click.echo(f"{prefix}{display}")


@cli.command()
@click.argument('name')
def use(name):
    """切换到指定配置"""
    cm = ConfigManager()
    if cm.set_active_config(name):
        config = cm.get_config(name)
        if config and (config["api_keys"] or config["auth_tokens"]):
            cm.update_env_file()
            display = format_config_display(name, config)
            click.echo(f"已切换到: {display}")

            # 检查是否需要手动激活环境变量
            # _show_manual_activation_hint(cm)
        else:
            click.echo(f"配置 '{name}' 没有可用的凭据")
    else:
        click.echo(f"配置 '{name}' 不存在", err=True)
        sys.exit(1)


def _show_manual_activation_hint(cm: ConfigManager):
    """显示手动激活环境变量的提示"""
    if cm.is_initialized() and not cm.is_wrapper_active():
        click.echo("\n💡 环境变量需要手动激活（因为shell集成尚未加载）:")
        click.echo("方法1 - 重新加载shell配置:")
        shell = os.environ.get('SHELL', '').split('/')[-1]
        if shell == 'zsh':
            click.echo("  source ~/.zshrc")
        elif shell == 'bash':
            click.echo("  source ~/.bashrc")
        else:
            click.echo("  source ~/.bashrc  # 或相应的shell配置文件")

        click.echo("\n方法2 - 立即激活当前配置的环境变量:")
        manual_cmd = cm.get_manual_activation_commands()
        if manual_cmd:
            click.echo(f"  {manual_cmd}")

        click.echo("\n方法3 - 使用eval命令:")
        click.echo(f"  eval $(cs current --export)")


@cli.command()
@click.option('--export', is_flag=True, help='输出可直接执行的export命令')
def current(export):
    """显示当前配置"""
    cm = ConfigManager()
    current_name = cm.get_current_config_name()
    if current_name:
        config = cm.get_config(current_name)
        if config:
            if export:
                export_cmd = cm.print_current_export()
                click.echo(export_cmd)
            else:
                display = format_config_display(current_name, config)
                click.echo(f"当前配置: {display}")
    else:
        click.echo("暂无激活配置")


@cli.command()
def add():
    """添加配置或凭据（交互式）"""
    cm = ConfigManager()
    configs = cm.get_configs()

    # 如果已有配置，提供选择：创建新配置还是添加凭据到已有配置
    if configs:
        click.echo("\n使用↑↓箭头键浏览，回车键确认选择，ESC键退出")
        
        action = _safe_questionary_select(
            "选择操作:",
            choices=[
                questionary.Choice("🆕 创建新配置", value="create_new"),
                questionary.Choice("🔑 添加凭据到已有配置", value="add_credential"),
            ]
        )

        if not action:
            click.echo("已取消操作")
            return

        if action == "add_credential":
            # 选择已有配置添加凭据
            config_name = select_config_for_credential(cm, configs)
            if config_name:
                add_credential_interactive(cm, config_name)
            else:
                click.echo("已取消添加凭据")
            return

    # 创建新配置的逻辑
    name = click.prompt("配置名称")
    if cm.get_config(name):
        click.echo(f"配置 '{name}' 已存在", err=True)
        return

    base_url = click.prompt("Base URL", default="https://api.anthropic.com")
    note = click.prompt("备注说明", default=name, show_default=False)

    if cm.add_config(name, base_url, note):
        click.echo(f"已添加配置: {name}")

        # 询问是否添加凭据
        if click.confirm("是否添加凭据?", default=True):
            add_credential_interactive(cm, name)
    else:
        click.echo("添加失败", err=True)


@cli.command()
@click.argument('name')
def edit(name):
    """编辑配置"""
    cm = ConfigManager()
    config = cm.get_config(name)
    if not config:
        click.echo(f"配置 '{name}' 不存在", err=True)
        return

    click.echo(f"正在编辑配置: {name}")

    # 基础信息
    base_url = click.prompt("Base URL", default=config['base_url'])
    note = click.prompt("备注说明", default=config['note'])

    if cm.get_config(name):
        # 更新基础信息
        config['base_url'] = base_url
        config['note'] = note
        cm._save_config(cm._load_config())
        click.echo(f"已更新配置: {name}")


@cli.command()
@click.argument('name', required=False)
def remove(name):
    """删除配置或凭据（交互式）"""
    cm = ConfigManager()

    if name:
        # 保持向后兼容：直接删除指定配置
        if click.confirm(f'确定要删除配置 "{name}" 吗？'):
            if cm.remove_config(name):
                click.echo(f"已删除配置: {name}")
            else:
                click.echo(f"删除失败或配置 '{name}' 不存在", err=True)
    else:
        # 无参数时进入交互式删除模式
        interactive_remove()


@cli.command()
def init():
    """初始化shell集成（自动生效）"""
    cm = ConfigManager()

    click.echo("🔧 正在初始化 claude-switch shell 集成...")
    click.echo("")

    result = cm.init_shell()
    click.echo(result)

    # 如果初始化成功，检查是否需要添加配置
    configs = cm.get_configs()
    if not configs or len(configs) == 0:
        click.echo("")
        click.echo("🎯 检测到尚无配置，建议立即添加一个配置：")
        if click.confirm("是否现在添加第一个配置？", default=True):
            # 调用添加配置的交互式流程
            add_first_config_interactive(cm)
    else:
        click.echo("")
        click.echo(f"📋 当前已有 {len(configs)} 个配置，可以直接使用 'cs' 命令选择")


@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='显示详细清理信息')
@click.option('--force', '-f', is_flag=True, help='跳过确认直接清理')
def cleanup(verbose, force):
    """清理所有创建的文件和配置（用于卸载）"""
    cm = ConfigManager()

    click.echo("🧹 Claude Switch 清理工具")
    click.echo("此命令将删除所有由 claude-switch 创建的文件和配置")
    click.echo("")

    # 显示将要清理的内容
    if cm.config_dir.exists():
        click.echo(f"📁 将删除配置目录: {cm.config_dir}")
    else:
        click.echo("📁 配置目录不存在")

    # 检查 shell 配置文件
    shell_config_map = {
        'bash': Path.home() / '.bashrc',
        'zsh': Path.home() / '.zshrc',
        'fish': Path.home() / '.config' / 'fish' / 'config.fish'
    }

    for shell_name, shell_config in shell_config_map.items():
        if shell_config.exists():
            with open(shell_config, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'Claude Switch' in content:
                click.echo(f"🔧 将清理 {shell_name} 配置: {shell_config}")

    click.echo("")
    click.echo("⚠️  警告：此操作不可撤销！")

    if not force:
        if not click.confirm("确定要继续清理吗？"):
            click.echo("❌ 已取消清理操作")
            return

    click.echo("")
    click.echo("🧹 开始清理...")

    success = cm.cleanup(verbose=verbose)

    if success:
        click.echo("")
        click.echo("✅ 清理完成！")
        click.echo("")
        click.echo("📝 后续步骤：")
        click.echo("   1. 重启终端或重新加载 shell 配置")
        click.echo("   2. 手动清理环境变量（如需要）：")
        click.echo("      unset ANTHROPIC_BASE_URL")
        click.echo("      unset ANTHROPIC_AUTH_TOKEN")
        click.echo("      unset ANTHROPIC_API_KEY")
    else:
        click.echo("")
        click.echo("❌ 清理过程中出现错误，请检查上述输出")


def add_first_config_interactive(cm: ConfigManager):
    """添加第一个配置的交互式流程"""
    click.echo("")
    click.echo("📝 添加第一个配置:")

    name = click.prompt("配置名称", default="default")
    base_url = click.prompt("Base URL", default="https://api.anthropic.com")
    note = click.prompt("备注说明", default=name, show_default=False)

    if cm.add_config(name, base_url, note):
        click.echo(f"✅ 已添加配置: {name}")

        # 询问是否添加凭据
        if click.confirm("是否添加凭据（API Key 或 Auth Token）？", default=True):
            add_credential_interactive(cm, name)

        # 自动激活刚添加的配置
        if cm.set_active_config(name):
            cm.update_env_file()
            click.echo(f"✅ 已激活配置: {name}")

            # 检查是否需要手动激活环境变量
            _show_manual_activation_hint(cm)

        click.echo("")
        click.echo("🎉 初始化完成！现在可以使用以下命令：")
        click.echo("   cs          # 交互式选择配置")
        click.echo("   cs list     # 查看所有配置")
        click.echo("   cs current  # 查看当前配置")
        click.echo("   cs --help   # 查看更多命令")
    else:
        click.echo("❌ 添加配置失败", err=True)


@cli.command()
@click.argument('config_name', required=False)
def add_credential(config_name):
    """添加凭据到配置"""
    cm = ConfigManager()
    
    # 如果没有指定配置名，让用户选择
    if not config_name:
        configs = cm.get_configs()
        if not configs:
            click.echo("暂无配置，请先使用 'cs add' 添加配置", err=True)
            return
            
        config_name = select_config_for_credential(cm, configs)
        if not config_name:
            click.echo("已取消添加凭据")
            return
    
    if not cm.get_config(config_name):
        click.echo(f"配置 '{config_name}' 不存在", err=True)
        return

    add_credential_interactive(cm, config_name)


# 添加 css 命令作为快捷方式
@cli.command('css')
@click.argument('config_name', required=False)
def css_add(config_name):
    """快速添加凭据到配置 (css = claude-switch add)"""
    # 直接调用 add_credential 的逻辑
    cm = ConfigManager()
    
    # 如果没有指定配置名，让用户选择
    if not config_name:
        configs = cm.get_configs()
        if not configs:
            click.echo("暂无配置，请先使用 'cs add' 添加配置", err=True)
            return
            
        config_name = select_config_for_credential(cm, configs)
        if not config_name:
            click.echo("已取消添加凭据")
            return
    
    if not cm.get_config(config_name):
        click.echo(f"配置 '{config_name}' 不存在", err=True)
        return

    add_credential_interactive(cm, config_name)


def interactive_select():
    """交互式选择配置（支持箭头键）"""
    cm = ConfigManager()
    configs = cm.get_configs()
    current = cm.get_current_config_name()

    if not configs:
        click.echo("暂无配置，请使用 'cs add' 添加")
        return

    # 准备选择列表
    choices = []
    current_choice = None  # 保存当前激活配置的Choice对象
    
    for name, config in configs.items():
        display = format_config_display(name, config)
        prefix = "→ " if name == current else "  "
        # 为当前激活的配置添加特殊标记，用于自定义样式
        if name == current:
            choice_text = f"✅ {display}"  # 使用勾号代替箭头，更清晰
        else:
            choice_text = f"  {display}"
        
        choice = questionary.Choice(
            choice_text,
            value=name
        )
        choices.append(choice)
        
        # 保存当前激活配置的Choice对象
        if name == current:
            current_choice = choice

    # 使用箭头键选择
    click.echo("\n使用↑↓箭头键浏览，回车键确认选择，ESC键退出")

    selected = _safe_questionary_select(
        "选择配置:",
        choices=choices,
        default=current_choice  # 使用Choice对象而不是字符串
    )

    if not selected:
        # 用户按ESC或取消了选择，直接退出
        click.echo("\n✗ 已取消配置选择")
        sys.exit(2)  # 设置退出码为2，表示用户取消，防止shell包装器显示成功提示

    if selected:
        # 保存原始配置状态，以便在取消时恢复
        original_config = cm.get_current_config_name()

        config = cm.get_config(selected)
        if config:
            # 先不切换配置，先让用户选择凭据
            if len(config["api_keys"]) + len(config["auth_tokens"]) > 1:
                click.echo(f"\n即将切换到配置: {selected}")
                click.echo("请选择要使用的凭据:")

                try:
                    credential_selected = select_credential_interactive(
                        cm, selected)

                    if credential_selected is not None:
                        # 用户确认了凭据选择，现在执行完整的切换
                        if cm.set_active_config(selected):
                            credential_type, index = credential_selected
                            cm.set_active_credential(
                                selected, credential_type, index)
                            cm.update_env_file()

                            display = format_config_display(selected, config)
                            click.echo(f"\n✓ 已完成切换到: {display}")

                            # 检查是否需要手动激活环境变量
                            # _show_manual_activation_hint(cm)
                        else:
                            click.echo("✗ 配置切换失败", err=True)
                    else:
                        # 用户取消了凭据选择，不执行配置切换
                        click.echo(f"\n✗ 已取消切换到配置: {selected}")
                        click.echo(f"保持当前配置: {original_config}")

                except KeyboardInterrupt:
                    # Ctrl+C 中断，不执行任何切换
                    click.echo(f"\n\n✗ 已取消切换到配置: {selected}")
                    click.echo(f"保持当前配置: {original_config}")
                    sys.exit(2)  # 设置退出码为2，表示用户取消，防止shell包装器显示成功提示
            else:
                # 只有一个凭据，直接切换
                if cm.set_active_config(selected):
                    cm.update_env_file()
                    display = format_config_display(selected, config)
                    click.echo(f"已切换到: {display}")

                    # 检查是否需要手动激活环境变量
                    # _show_manual_activation_hint(cm)
                else:
                    click.echo("配置切换失败", err=True)


def _build_credential_choices(config: Dict[str, Any], active_label: str = "默认激活") -> List[questionary.Choice]:
    """构建凭据选择列表的公共函数"""
    choices = []

    # 添加auth tokens
    for i, token in enumerate(config["auth_tokens"]):
        is_active = config["active_auth"] == i
        masked, display_name = parse_credential_with_name(token)
        display_text = f"{masked} ({display_name})" if display_name else masked

        if is_active:
            choice_text = f"✅ Auth Token {i+1}: {display_text} [{active_label}]"
        else:
            choice_text = f"  Auth Token {i+1}: {display_text}"

        choices.append(questionary.Choice(
            choice_text,
            value=("auth_token", i)
        ))

    # 添加api keys
    for i, key in enumerate(config["api_keys"]):
        is_active = config["active_key"] == i
        masked, display_name = parse_credential_with_name(key)
        display_text = f"{masked} ({display_name})" if display_name else masked

        if is_active:
            choice_text = f"✅ API Key {i+1}: {display_text} [{active_label}]"
        else:
            choice_text = f"  API Key {i+1}: {display_text}"

        choices.append(questionary.Choice(
            choice_text,
            value=("api_key", i)
        ))

    return choices


def _get_questionary_style() -> questionary.Style:
    """获取统一的 questionary 样式"""
    return questionary.Style([
        ('qmark', 'fg:#673ab7 bold'),
        ('question', 'bold'),
        ('answer', 'fg:#f44336 bold'),
        ('pointer', 'fg:#00aa00 bold'),
        ('highlighted', 'fg:#ffffff bold bg:#006600'),
        ('selected', 'fg:#cc5454'),
        ('separator', 'fg:#cc5454'),
        ('instruction', ''),
        ('text', ''),
        ('disabled', 'fg:#858585 italic')
    ])


def _safe_questionary_select(message: str, choices: List[questionary.Choice],
                             default=None, style=None) -> Optional[str]:
    """安全的 questionary select，确保ESC键正常工作"""
    try:
        result = questionary.select(
            message,
            choices=choices,
            default=default,
            style=style or _get_questionary_style(),
            # 优化参数提高兼容性和可靠性
            use_shortcuts=False,    # 禁用快捷键避免冲突
            use_indicator=True,     # 显示指示器
            show_selected=True      # 显示选中状态
        ).ask()

        # questionary 在ESC时可能返回None或空字符串
        return result if result else None

    except (KeyboardInterrupt, EOFError, Exception):
        # 处理各种中断情况:
        # - KeyboardInterrupt: Ctrl+C 或某些情况下的ESC键
        # - EOFError: 输入流结束
        # - Exception: 其他可能的异常（如某些终端环境下的ESC键处理）
        return None


def select_credential_interactive(cm: ConfigManager, config_name: str):
    """交互式选择凭据（预览模式，用于配置切换）"""
    config = cm.get_config(config_name)
    if not config or (len(config["api_keys"]) + len(config["auth_tokens"]) <= 1):
        return None

    choices = _build_credential_choices(config, "默认激活")

    if choices:
        click.echo("\n使用↑↓箭头键浏览，回车键确认选择，ESC键退出")
        click.echo("⚠️  注意: 只有按回车键确认选择才会执行配置切换")

        selected = _safe_questionary_select(
            f"选择 {config_name} 的凭据:",
            choices=choices
        )

        return selected  # 返回选择结果，不直接修改配置

    return None


def add_credential_interactive(cm: ConfigManager, config_name: str):
    """交互式添加凭据"""
    config = cm.get_config(config_name)
    if not config:
        return

    default_credential_type = None

    while True:
        click.echo("\n使用↑↓箭头键浏览，回车键确认选择，ESC键退出")

        credential_type = _safe_questionary_select(
            "选择凭据类型:",
            choices=[
                questionary.Choice("Auth Token", value="auth_token"),
                questionary.Choice("API Key", value="api_key")
            ],
            default=default_credential_type
        )

        if not credential_type:
            break

        # 记住当前选择的类型，用于下次默认
        default_credential_type = credential_type

        click.echo(f"\n💡 支持多种输入方式:")
        click.echo(f"  • 单个凭据: sk-ant-xxx")
        click.echo(f"  • 带自定义名称: sk-ant-xxx|production")
        click.echo(f"  • 多个凭据（逗号分割）: sk-ant-xxx|prod,sk-ant-yyy|dev")
        click.echo(f"  • 多个凭据（空格分割）: sk-ant-xxx|prod sk-ant-yyy|dev")

        value = click.prompt(f"输入 {credential_type}")
        if value:
            # 解析多个凭据
            credentials = parse_multiple_credentials(value)
            added_count = 0
            
            for credential in credentials:
                if credential.strip():
                    if cm.add_credential(config_name, credential_type, credential.strip()):
                        added_count += 1
                    else:
                        click.echo(f"⚠️  跳过重复凭据: {mask_credential(credential.strip().split('|')[0])}")
            
            if added_count > 0:
                click.echo(f"✅ 已成功添加 {added_count} 个 {credential_type}")
            else:
                click.echo(f"❌ 没有添加任何新凭据")

        if not click.confirm("继续添加更多凭据?", default=True):
            break


def parse_multiple_credentials(input_value: str) -> List[str]:
    """解析多个凭据输入，支持逗号和空格分割"""
    # 首先按逗号分割
    parts = input_value.split(',')
    
    # 如果只有一个部分，再尝试按空格分割
    if len(parts) == 1:
        # 检查是否包含空格且不是在名称部分（|后面）
        if ' ' in input_value and '|' in input_value:
            # 对于带名称的情况，需要更careful的处理
            # 简单策略：如果包含|，先看看是否是多个带名称的凭据
            space_parts = input_value.split(' ')
            # 检查每个部分是否都像是凭据（包含合理的前缀）
            if all(part.strip() and (part.strip().startswith(('sk-', 'ant-', 'claude-')) or '|' in part) for part in space_parts if part.strip()):
                parts = space_parts
        elif ' ' in input_value:
            # 没有|的情况，直接按空格分割
            parts = input_value.split(' ')
    
    # 清理并返回非空部分
    return [part.strip() for part in parts if part.strip()]


def select_config_for_credential(cm: ConfigManager, configs: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """选择配置来添加凭据"""
    current = cm.get_current_config_name()

    choices = []
    for name, config in configs.items():
        display = format_config_display(name, config)
        if name == current:
            choice_text = f"✅ {display}"
        else:
            choice_text = f"  {display}"
        choices.append(questionary.Choice(choice_text, value=name))

    click.echo("\n使用↑↓箭头键浏览，回车键确认选择，ESC键退出")

    selected = _safe_questionary_select(
        "选择要添加凭据的配置:",
        choices=choices,
        default=current
    )

    return selected


def format_config_display(name: str, config: Dict[str, Any]) -> str:
    """格式化配置显示"""
    base_url = config["base_url"]
    note = config["note"]

    # 计算凭据数量
    key_count = len(config["api_keys"])
    token_count = len(config["auth_tokens"])

    # 显示激活的凭据，包括名称支持
    active_display = ""
    if config["active_auth"] >= 0 and config["active_auth"] < token_count:
        token_value = config["auth_tokens"][config["active_auth"]]
        if '|' in token_value:
            _, name_part = token_value.split('|', 1)
            active_display = f"token{config['active_auth']+1}({name_part})"
        else:
            active_display = f"token{config['active_auth']+1}"
    elif config["active_key"] >= 0 and config["active_key"] < key_count:
        key_value = config["api_keys"][config["active_key"]]
        if '|' in key_value:
            _, name_part = key_value.split('|', 1)
            active_display = f"key{config['active_key']+1}({name_part})"
        else:
            active_display = f"key{config['active_key']+1}"
    else:
        active_display = "未设置"

    credentials_info = f"({token_count}tokens, {key_count}keys) [{active_display}]"

    return f"{name} - {note} [{base_url}] {credentials_info}"


def parse_credential_with_name(value: str) -> tuple[str, str]:
    """解析带名称的凭据，返回(masked_credential, name)"""
    if '|' in value:
        credential, name = value.split('|', 1)
        return mask_credential(credential), name
    else:
        return mask_credential(value), ""


def mask_credential(value: str) -> str:
    """掩码显示凭据"""
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def interactive_remove():
    """交互式删除主流程"""
    cm = ConfigManager()
    configs = cm.get_configs()

    if not configs:
        click.echo("暂无配置可删除")
        return

    if len(configs) <= 1:
        click.echo("至少需要保留一个配置，无法删除")
        return

    # 第一步：选择配置
    selected_config = select_config_for_removal(cm, configs)
    if not selected_config:
        return

    # 第二步：选择操作类型
    while True:
        action = select_removal_action(selected_config)
        if not action:
            # ESC返回配置选择
            selected_config = select_config_for_removal(cm, configs)
            if not selected_config:
                return
            continue

        if action == "delete_config":
            # 删除整个配置
            if confirm_and_remove_config(cm, selected_config):
                return
            # 如果取消删除，返回操作选择
            continue

        elif action == "delete_credential":
            # 删除凭据
            config = cm.get_config(selected_config)
            if not config or (len(config["api_keys"]) + len(config["auth_tokens"])) == 0:
                click.echo(f"配置 '{selected_config}' 没有凭据可删除")
                continue

            result = remove_credential_interactive(cm, selected_config)
            if result == "back":
                # 返回操作选择
                continue
            elif result == "deleted":
                # 删除成功，询问是否继续
                if not click.confirm("是否继续删除其他项目？", default=False):
                    return
                continue
            else:
                # 取消或其他情况，返回配置选择
                selected_config = select_config_for_removal(cm, configs)
                if not selected_config:
                    return
                continue


def select_config_for_removal(cm: ConfigManager, configs: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """选择要删除的配置"""
    current = cm.get_current_config_name()

    choices = []
    for name, config in configs.items():
        display = format_config_display(name, config)
        if name == current:
            choice_text = f"✅ {display}"
        else:
            choice_text = f"  {display}"
        choices.append(questionary.Choice(choice_text, value=name))

    click.echo("\n使用↑↓箭头键浏览，回车键确认选择，ESC键退出")

    selected = _safe_questionary_select(
        "选择要操作的配置:",
        choices=choices
    )

    if not selected:
        click.echo("\n✗ 已退出删除操作")

    return selected


def select_removal_action(config_name: str) -> Optional[str]:
    """选择删除操作类型"""
    choices = [
        questionary.Choice("🔑 删除配置中的凭据", value="delete_credential"),
        questionary.Choice(
            f"🗑️  删除整个配置 \"{config_name}\"", value="delete_config"),
    ]

    click.echo("\n使用↑↓箭头键浏览，回车键确认选择，ESC键返回配置选择")

    selected = _safe_questionary_select(
        f"选择对配置 \"{config_name}\" 的操作:",
        choices=choices
    )

    return selected  # 返回None表示ESC，调用方处理返回上一步


def remove_credential_interactive(cm: ConfigManager, config_name: str) -> str:
    """交互式删除凭据"""
    config = cm.get_config(config_name)
    if not config:
        return "error"

    choices = _build_credential_choices(config, "当前激活")

    if not choices:
        click.echo(f"配置 '{config_name}' 没有凭据可删除")
        return "back"

    click.echo("\n使用↑↓箭头键浏览，回车键确认选择，ESC键返回操作选择")

    selected = _safe_questionary_select(
        f"选择要删除的凭据 (配置: {config_name}):",
        choices=choices
    )

    if selected:
        credential_type, index = selected

        # 显示要删除的凭据信息
        if credential_type == "auth_token":
            credential_value = config["auth_tokens"][index]
            type_display = "Auth Token"
        else:
            credential_value = config["api_keys"][index]
            type_display = "API Key"

        masked, name = parse_credential_with_name(credential_value)
        display_text = f"{masked} ({name})" if name else masked

        # 检查是否是当前激活的凭据
        is_active = False
        if credential_type == "auth_token" and config["active_auth"] == index:
            is_active = True
        elif credential_type == "api_key" and config["active_key"] == index:
            is_active = True

        active_warning = "\n⚠️  警告: 这是当前激活的凭据，删除后将自动切换到其他凭据" if is_active else ""

        click.echo(f"\n即将删除:")
        click.echo(f"  配置: {config_name}")
        click.echo(f"  类型: {type_display} {index + 1}")
        click.echo(f"  内容: {display_text}")
        click.echo(active_warning)

        if click.confirm(f"\n确定要删除这个{type_display.lower()}吗？", default=False):
            if cm.remove_credential(config_name, credential_type, index):
                # 如果删除的是当前激活配置的凭据，更新环境变量
                if config_name == cm.get_current_config_name():
                    cm.update_env_file()

                click.echo(f"✅ 已删除 {type_display.lower()}: {display_text}")
                return "deleted"
            else:
                click.echo(f"❌ 删除失败")
                return "back"
        else:
            click.echo("✗ 已取消删除")
            return "back"
    else:
        # 用户按ESC返回
        return "back"


def confirm_and_remove_config(cm: ConfigManager, config_name: str) -> bool:
    """确认并删除配置"""
    config = cm.get_config(config_name)
    if not config:
        click.echo(f"配置 '{config_name}' 不存在")
        return False

    current = cm.get_current_config_name()
    is_current = config_name == current

    # 显示要删除的配置详细信息
    display = format_config_display(config_name, config)

    click.echo(f"\n即将删除整个配置:")
    click.echo(f"  {display}")

    if is_current:
        click.echo("⚠️  警告: 这是当前激活的配置，删除后将自动切换到其他配置")

    # 显示凭据数量
    total_credentials = len(config["api_keys"]) + len(config["auth_tokens"])
    if total_credentials > 0:
        click.echo(f"⚠️  警告: 将同时删除 {total_credentials} 个凭据")

    if click.confirm(f"\n确定要删除配置 \"{config_name}\" 吗？这个操作不可撤销！", default=False):
        if cm.remove_config(config_name):
            # 如果删除的是当前激活配置，更新环境变量
            if is_current:
                cm.update_env_file()

            click.echo(f"✅ 已删除配置: {config_name}")
            return True
        else:
            click.echo("❌ 删除失败")
            return False
    else:
        click.echo("✗ 已取消删除")
        return False


if __name__ == '__main__':
    cli()
