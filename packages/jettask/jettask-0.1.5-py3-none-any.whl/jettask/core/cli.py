#!/usr/bin/env python
"""
JetTask CLI - 命令行接口
"""
import click
import sys
import os
import importlib
import importlib.util
import json
from pathlib import Path

@click.group()
@click.version_option(version='0.1.0', prog_name='JetTask')
def cli():
    """JetTask - 高性能分布式任务队列系统"""
    pass

@cli.command()
@click.option('--host', default='0.0.0.0', help='服务器监听地址')
@click.option('--port', default=8001, type=int, help='服务器监听端口')
def webui(host, port):
    """启动 Web UI 监控界面"""
    from jettask.webui.backend.main import run_server
    click.echo(f"Starting JetTask Web UI on {host}:{port}")
    
    # 修改端口设置
    import uvicorn
    uvicorn.run(
        "jettask.webui.backend.main:app",
        host=host,
        port=port,
        log_level="info"
    )

def load_module_from_path(module_path: str):
    """从文件路径加载 Python 模块"""
    path = Path(module_path).resolve()
    
    if not path.exists():
        raise FileNotFoundError(f"Module file not found: {module_path}")
    
    # 获取模块名
    module_name = path.stem
    
    # 加载模块
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None:
        raise ImportError(f"Cannot load module from {module_path}")
    
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    return module

def find_jettask_app(module):
    """在模块中查找 Jettask 实例"""
    from jettask import Jettask
    
    # 查找模块中的 Jettask 实例
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, Jettask):
            return obj
    
    # 如果没有找到，尝试查找名为 'app' 的变量
    if hasattr(module, 'app'):
        obj = getattr(module, 'app')
        if isinstance(obj, Jettask):
            return obj
    
    return None

@cli.command()
@click.argument('app_str')
@click.option('--queues', '-q', required=True, help='队列名称（逗号分隔，如: queue1,queue2）')
@click.option('--executor', '-e', 
              type=click.Choice(['asyncio', 'multi_asyncio']),
              default='asyncio',
              help='执行器类型')
@click.option('--concurrency', '-c', type=int, default=4, help='并发数')
@click.option('--prefetch', '-p', type=int, default=100, help='预取倍数')
@click.option('--reload', '-r', is_flag=True, help='自动重载')
@click.option('--config', help='配置文件 (JSON格式)')
def worker(app_str, queues, executor, concurrency, prefetch, reload, config):
    """启动任务处理 Worker
    
    示例:
    \b
      jettask worker main:app --queues async_queue
      jettask worker tasks.py:app --queues queue1,queue2,queue3
      jettask worker myapp.tasks:app --queues high,normal,low --executor multi_asyncio
    """
    
    # 如果提供了配置文件，从中加载配置
    if config:
        click.echo(f"Loading configuration from {config}")
        with open(config, 'r') as f:
            config_data = json.load(f)
        
        # 从配置文件读取参数（命令行参数优先）
        queues = queues or ','.join(config_data.get('queues', [])) if config_data.get('queues') else None
        executor = executor or config_data.get('executor', 'asyncio')
        concurrency = concurrency if concurrency != 4 else config_data.get('concurrency', 4)
        prefetch = prefetch if prefetch != 100 else config_data.get('prefetch', 100)
        reload = reload or config_data.get('reload', False)
    
    # 解析 app_str (格式: module:app_name 或 file.py:app_name)
    module = None
    file = None
    app_name = 'app'
    
    if ':' in app_str:
        module_or_file, app_name = app_str.split(':', 1)
        
        # 判断是文件还是模块
        if module_or_file.endswith('.py') or '/' in module_or_file or os.path.exists(module_or_file):
            # 如果是文件路径（包含 / 或 .py 结尾，或者文件存在）
            file = module_or_file
            # 如果没有 .py 后缀，尝试添加
            if not file.endswith('.py') and os.path.exists(file + '.py'):
                file = file + '.py'
        else:
            # 否则作为模块名处理（如 myapp.tasks）
            module = module_or_file
    else:
        # 如果没有冒号，判断是文件还是模块
        if app_str.endswith('.py') or '/' in app_str or os.path.exists(app_str):
            file = app_str
            if not file.endswith('.py') and os.path.exists(file + '.py'):
                file = file + '.py'
        else:
            module = app_str
    
    # 解析队列列表（支持逗号分隔）
    queue_list = [q.strip() for q in queues.split(',') if q.strip()]
    
    if not queue_list:
        click.echo("Error: Must specify at least one queue with --queues", err=True)
        click.echo("  Example: --queues queue1,queue2,queue3", err=True)
        sys.exit(1)
    
    # 加载模块
    try:
        if file:
            click.echo(f"Loading tasks from file: {file}")
            loaded_module = load_module_from_path(file)
        else:
            click.echo(f"Loading tasks from module: {module}")
            loaded_module = importlib.import_module(module)
        
        # 查找 Jettask 实例
        app = find_jettask_app(loaded_module)
        
        if not app:
            # 如果自动查找失败，尝试使用指定的名称
            if hasattr(loaded_module, app_name):
                app = getattr(loaded_module, app_name)
            else:
                click.echo(f"Error: Cannot find Jettask instance '{app_name}' in the module", err=True)
                sys.exit(1)
        
        click.echo(f"Found Jettask app: {app}")
        
    except ImportError as e:
        import traceback
        traceback.print_exc()
        click.echo(f"Error loading module: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    
    # 从 app 实例中获取实际配置
    redis_url = app.redis_url if hasattr(app, 'redis_url') else 'Not configured'
    redis_prefix = app.redis_prefix if hasattr(app, 'redis_prefix') else 'jettask'
    consumer_strategy = app.consumer_strategy if hasattr(app, 'consumer_strategy') else 'heartbeat'
    
    # 显示配置信息
    click.echo("=" * 60)
    click.echo("JetTask Worker Configuration")
    click.echo("=" * 60)
    click.echo(f"App:          {app_str}")
    click.echo(f"Redis URL:    {redis_url}")
    click.echo(f"Redis Prefix: {redis_prefix}")
    click.echo(f"Strategy:     {consumer_strategy}")
    click.echo(f"Queues:       {', '.join(queue_list)}")
    click.echo(f"Executor:     {executor}")
    click.echo(f"Concurrency:  {concurrency}")
    click.echo(f"Prefetch:     {prefetch}")
    click.echo(f"Auto-reload:  {reload}")
    click.echo("=" * 60)
    
    # 启动 Worker
    try:
        click.echo(f"Starting {executor} worker...")
        app.start(
            execute_type=executor,
            queues=queue_list,
            concurrency=concurrency,
            prefetch_multiplier=prefetch,
            reload=reload
        )
    except KeyboardInterrupt:
        click.echo("\nShutting down worker...")
    except Exception as e:
        click.echo(f"Error starting worker: {e}", err=True)
        sys.exit(1)

@cli.command('webui-consumer')
@click.option('--pg-url', help='PostgreSQL URL (optional, will use env var if not provided)')
def webui_consumer(pg_url):
    """启动 Web UI 数据消费者（同步 Redis 数据到 PostgreSQL）"""
    click.echo("Starting WebUI Consumer...")
    
    import os
    if pg_url:
        os.environ['JETTASK_PG_URL'] = pg_url
    
    # 启动 pg_consumer (它会从环境变量读取 Redis 配置)
    from jettask.webui.pg_consumer import main as consumer_main
    consumer_main()

@cli.command()
def monitor():
    """启动系统监控器"""
    click.echo("Starting JetTask Monitor")
    from jettask.webui.run_monitor import main as monitor_main
    monitor_main()

@cli.command()
def init():
    """初始化数据库和配置"""
    click.echo("Initializing JetTask...")
    
    # 初始化数据库
    from jettask.webui.db_init import init_database
    click.echo("Initializing database...")
    init_database()
    
    click.echo("JetTask initialized successfully!")

@cli.command()
def status():
    """显示系统状态"""
    click.echo("JetTask System Status")
    click.echo("=" * 50)
    
    # 检查 Redis 连接
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        click.echo("✓ Redis: Connected")
    except:
        click.echo("✗ Redis: Not connected")
    
    # 检查 PostgreSQL 连接
    try:
        import psycopg2
        conn = psycopg2.connect(
            dbname=os.getenv('JETTASK_PG_DB', 'jettask'),
            user=os.getenv('JETTASK_PG_USER', 'jettask'),
            password=os.getenv('JETTASK_PG_PASSWORD', '123456'),
            host=os.getenv('JETTASK_PG_HOST', 'localhost'),
            port=os.getenv('JETTASK_PG_PORT', '5432')
        )
        conn.close()
        click.echo("✓ PostgreSQL: Connected")
    except:
        click.echo("✗ PostgreSQL: Not connected")
    
    click.echo("=" * 50)

def main():
    """主入口函数"""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()