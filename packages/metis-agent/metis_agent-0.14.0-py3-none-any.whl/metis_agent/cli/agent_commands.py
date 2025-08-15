"""
Multi-Agent Management CLI Commands

Provides comprehensive command-line interface for managing multi-agent systems,
including agent creation, knowledge management, memory isolation, and collaboration.
"""
import os
import json
import time
import click
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from ..core.agent_manager import get_agent_manager, configure_agent_manager
from ..memory.isolated_memory import get_memory_manager, configure_memory_manager
from ..knowledge.shared_knowledge import get_shared_knowledge, configure_shared_knowledge
from ..config.agent_profiles import ProfileManager

# Try to import Rich for enhanced visuals
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.tree import Tree
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.status import Status
    from rich.text import Text
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


def rich_print(text: str, style: str = None):
    """Print with Rich formatting if available, fallback to plain print."""
    if RICH_AVAILABLE and console:
        if style:
            console.print(text, style=style)
        else:
            console.print(text)
    else:
        print(text)


def create_table(title: str, columns: List[str]) -> Any:
    """Create a Rich table if available, return None otherwise."""
    if RICH_AVAILABLE:
        table = Table(title=title, show_header=True, header_style="bold magenta")
        for column in columns:
            table.add_column(column)
        return table
    return None


@click.group(name='agents')
def agent_group():
    """Multi-agent system management commands."""
    pass


@agent_group.command()
@click.option('--max-agents', '-m', default=10, help='Maximum number of concurrent agents')
@click.option('--shared-knowledge', '-k', is_flag=True, help='Enable shared knowledge base')
@click.option('--memory-isolation', '-i', is_flag=True, help='Enable memory isolation')
@click.option('--config-file', '-c', help='Configuration file path')
def init(max_agents: int, shared_knowledge: bool, memory_isolation: bool, config_file: str):
    """Initialize the multi-agent system."""
    rich_print("🚀 Initializing Multi-Agent System", "bold blue")
    
    try:
        # Initialize agent manager
        with Status("Setting up Agent Manager...") if RICH_AVAILABLE else None:
            agent_manager = configure_agent_manager(
                max_agents=max_agents,
                shared_knowledge_enabled=shared_knowledge
            )
        
        # Initialize shared knowledge if enabled
        if shared_knowledge:
            with Status("Setting up Shared Knowledge Base...") if RICH_AVAILABLE else None:
                configure_shared_knowledge("knowledge/shared_knowledge.db")
            rich_print("✅ Shared Knowledge Base initialized", "green")
        
        # Initialize memory isolation if enabled
        if memory_isolation:
            with Status("Setting up Memory Isolation...") if RICH_AVAILABLE else None:
                configure_memory_manager("memory/agents")
            rich_print("✅ Memory Isolation initialized", "green")
        
        rich_print(f"✅ Multi-Agent System initialized with max {max_agents} agents", "green")
        
        # Display system info
        if RICH_AVAILABLE:
            panel = Panel.fit(
                f"[bold]Multi-Agent System Ready[/bold]\n\n"
                f"Max Agents: {max_agents}\n"
                f"Shared Knowledge: {'Enabled' if shared_knowledge else 'Disabled'}\n"
                f"Memory Isolation: {'Enabled' if memory_isolation else 'Disabled'}\n"
                f"Initialized at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                title="System Status",
                border_style="green"
            )
            console.print(panel)
        
    except Exception as e:
        rich_print(f"❌ Failed to initialize multi-agent system: {e}", "red")


@agent_group.command()
@click.argument('agent_id')
@click.option('--profile', '-p', help='Agent profile name or path')
@click.option('--memory-limit', '-m', default=100.0, help='Memory limit in MB')
@click.option('--isolation-level', '-l', 
              type=click.Choice(['strict', 'moderate', 'permissive']), 
              default='moderate', help='Memory isolation level')
@click.option('--allowed-categories', '-c', multiple=True, help='Allowed knowledge categories')
def create(agent_id: str, profile: str, memory_limit: float, isolation_level: str, allowed_categories: tuple):
    """Create a new agent."""
    rich_print(f"🤖 Creating agent: {agent_id}", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            rich_print("❌ Agent manager not initialized. Run 'agents init' first.", "red")
            return
        
        # Load profile if specified
        profile_config = {
            'name': agent_id,
            'description': f'Agent {agent_id} created via CLI',
            'version': '1.0.0',
            'llm_provider': 'openai',
            'llm_model': 'gpt-3.5-turbo',
            'system_message': f'You are {agent_id}, an AI assistant specialized in your designated tasks.',
            'tools': {
                'enabled': ['CalculatorTool', 'CodingTool', 'EditTool'],
                'disabled': [],
                'config': {}
            },
            'memory': {
                'enabled': True,
                'type': 'sqlite'
            }
        }
        
        if profile:
            profile_manager = ProfileManager()
            try:
                if os.path.exists(profile):
                    # Load from file path
                    loaded_profile = profile_manager.load_profile(profile)
                else:
                    # Try to load by name
                    loaded_profile = profile_manager.load_profile(profile)
                
                # Convert AgentProfile to dict and transform for AgentManager
                if hasattr(loaded_profile, '__dict__'):
                    loaded_config = loaded_profile.__dict__
                    
                    # Transform the profile format to match AgentManager expectations
                    if 'llm_config' in loaded_config and loaded_config['llm_config']:
                        llm_config = loaded_config['llm_config']
                        if hasattr(llm_config, '__dict__'):
                            llm_config = llm_config.__dict__
                        profile_config['llm_provider'] = llm_config.get('provider', 'openai')
                        profile_config['llm_model'] = llm_config.get('model', 'gpt-3.5-turbo')
                    
                    # Transform tools format
                    if 'tools' in loaded_config and loaded_config['tools']:
                        tools_config = loaded_config['tools']
                        if hasattr(tools_config, 'enabled'):
                            profile_config['enabled_tools'] = tools_config.enabled
                        elif hasattr(tools_config, '__dict__'):
                            tools_dict = tools_config.__dict__
                            profile_config['enabled_tools'] = tools_dict.get('enabled', [])
                    
                    # Update other fields
                    profile_config.update({k: v for k, v in loaded_config.items() 
                                         if k not in ['llm_config', 'tools']})
                else:
                    loaded_config = loaded_profile
                    profile_config.update(loaded_config)
            except Exception as e:
                rich_print(f"❌ Failed to load profile '{profile}': {e}", "red")
                return
        
        # Configure memory settings
        memory_config = {
            'max_memory_mb': memory_limit,
            'isolation_level': isolation_level,
            'allowed_shared_keys': [f'shared.{cat}' for cat in allowed_categories],
            'restricted_keys': ['sensitive.*', 'private.*']
        }
        
        # Create agent
        agent_id_result = agent_manager.create_agent(
            profile_name=profile or 'default',
            agent_id=agent_id,
            profile_config=profile_config,
            memory_config=memory_config
        )
        
        if agent_id_result:
            rich_print(f"✅ Agent '{agent_id}' created successfully", "green")
            
            # Display agent info
            if RICH_AVAILABLE:
                table = create_table(f"Agent: {agent_id}", ["Property", "Value"])
                table.add_row("Profile", profile or "Default")
                table.add_row("Memory Limit", f"{memory_limit} MB")
                table.add_row("Isolation Level", isolation_level)
                table.add_row("Allowed Categories", ", ".join(allowed_categories) or "None")
                table.add_row("Status", "Active")
                console.print(table)
        else:
            rich_print(f"❌ Failed to create agent '{agent_id}'", "red")
            
    except Exception as e:
        rich_print(f"❌ Error creating agent: {e}", "red")


@agent_group.command()
def list():
    """List all active agents."""
    rich_print("📋 Active Agents", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            rich_print("❌ Agent manager not initialized", "red")
            return
        
        agents = agent_manager.list_agents()
        
        if not agents:
            rich_print("No active agents found", "yellow")
            return
        
        if RICH_AVAILABLE:
            table = create_table("Active Agents", [
                "Agent ID", "Profile", "Status", "Memory Usage", "Tasks", "Last Active"
            ])
            
            for agent_id in agents:
                agent_info = agent_manager.get_agent_info(agent_id)
                memory_stats = agent_manager.get_agent_memory_stats(agent_id)
                
                memory_usage = f"{memory_stats.get('memory_size_mb', 0):.1f} MB" if memory_stats else "N/A"
                last_active = agent_info.get('last_active', 'Never')
                if isinstance(last_active, (int, float)):
                    last_active = datetime.fromtimestamp(last_active).strftime('%H:%M:%S')
                
                table.add_row(
                    agent_id,
                    agent_info.get('profile', 'Default'),
                    agent_info.get('status', 'Unknown'),
                    memory_usage,
                    str(agent_info.get('task_count', 0)),
                    last_active
                )
            
            console.print(table)
        else:
            for agent_id in agents:
                print(f"- {agent_id}")
                
    except Exception as e:
        rich_print(f"❌ Error listing agents: {e}", "red")


@agent_group.command()
@click.argument('agent_id')
@click.option('--force', '-f', is_flag=True, help='Force stop without cleanup')
def stop(agent_id: str, force: bool):
    """Stop an agent."""
    rich_print(f"🛑 Stopping agent: {agent_id}", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            rich_print("❌ Agent manager not initialized", "red")
            return
        
        success = agent_manager.stop_agent(agent_id, force=force)
        
        if success:
            rich_print(f"✅ Agent '{agent_id}' stopped successfully", "green")
        else:
            rich_print(f"❌ Failed to stop agent '{agent_id}'", "red")
            
    except Exception as e:
        rich_print(f"❌ Error stopping agent: {e}", "red")


@agent_group.command()
@click.argument('agent_id')
def status(agent_id: str):
    """Get detailed status of an agent."""
    rich_print(f"📊 Agent Status: {agent_id}", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        if not agent_manager:
            rich_print("❌ Agent manager not initialized", "red")
            return
        
        if agent_id not in agent_manager.list_agents():
            rich_print(f"❌ Agent '{agent_id}' not found", "red")
            return
        
        # Get comprehensive agent info
        agent_info = agent_manager.get_agent_info(agent_id)
        memory_stats = agent_manager.get_agent_memory_stats(agent_id)
        
        if RICH_AVAILABLE:
            # Agent basic info
            info_table = create_table(f"Agent: {agent_id}", ["Property", "Value"])
            info_table.add_row("Status", agent_info.get('status', 'Unknown'))
            info_table.add_row("Profile", agent_info.get('profile', 'Default'))
            info_table.add_row("Created", agent_info.get('created_at', 'Unknown'))
            info_table.add_row("Last Active", agent_info.get('last_active', 'Never'))
            info_table.add_row("Task Count", str(agent_info.get('task_count', 0)))
            
            console.print(info_table)
            
            # Memory statistics
            if memory_stats:
                memory_table = create_table("Memory Statistics", ["Metric", "Value"])
                memory_table.add_row("Memory Usage", f"{memory_stats.get('memory_size_mb', 0):.2f} MB")
                memory_table.add_row("Entries", str(memory_stats.get('entry_count', 0)))
                memory_table.add_row("Access Count", str(memory_stats.get('access_count', 0)))
                memory_table.add_row("Cache Hit Rate", f"{memory_stats.get('cache_hit_rate', 0):.1%}")
                memory_table.add_row("Shared Accesses", str(memory_stats.get('shared_accesses', 0)))
                
                console.print(memory_table)
        else:
            print(f"Agent: {agent_id}")
            print(f"Status: {agent_info.get('status', 'Unknown')}")
            print(f"Memory Usage: {memory_stats.get('memory_size_mb', 0):.2f} MB" if memory_stats else "Memory: N/A")
            
    except Exception as e:
        rich_print(f"❌ Error getting agent status: {e}", "red")


@agent_group.command()
@click.argument('from_agent')
@click.argument('to_agent') 
@click.argument('knowledge_key')
@click.argument('knowledge_data')
@click.option('--metadata', '-m', help='JSON metadata for the knowledge')
def share(from_agent: str, to_agent: str, knowledge_key: str, knowledge_data: str, metadata: str):
    """Share knowledge between agents."""
    rich_print(f"🔄 Sharing knowledge: {from_agent} → {to_agent}", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        memory_manager = get_memory_manager()
        
        if not agent_manager or not memory_manager:
            rich_print("❌ System not initialized", "red")
            return
        
        # Parse knowledge data
        try:
            if knowledge_data.startswith('{') or knowledge_data.startswith('['):
                data = json.loads(knowledge_data)
            else:
                data = knowledge_data
        except json.JSONDecodeError:
            data = knowledge_data
        
        # Parse metadata
        meta = {}
        if metadata:
            try:
                meta = json.loads(metadata)
            except json.JSONDecodeError:
                rich_print("❌ Invalid JSON metadata", "red")
                return
        
        # Share knowledge
        success = memory_manager.share_knowledge(
            from_agent, to_agent, knowledge_key, data, meta
        )
        
        if success:
            rich_print(f"✅ Knowledge '{knowledge_key}' shared successfully", "green")
        else:
            rich_print(f"❌ Failed to share knowledge", "red")
            
    except Exception as e:
        rich_print(f"❌ Error sharing knowledge: {e}", "red")


@agent_group.command()
@click.option('--category', '-c', help='Filter by knowledge category')
@click.option('--agent', '-a', help='Filter by agent access')
@click.option('--limit', '-l', default=20, help='Maximum number of results')
def knowledge(category: str, agent: str, limit: int):
    """List shared knowledge entries."""
    rich_print("🧠 Shared Knowledge Base", "bold blue")
    
    try:
        shared_kb = get_shared_knowledge()
        if not shared_kb:
            rich_print("❌ Shared knowledge base not initialized", "red")
            return
        
        # Query knowledge
        results = shared_kb.query_knowledge(
            category=category,
            agent_id=agent,
            limit=limit
        )
        
        if not results:
            rich_print("No knowledge entries found", "yellow")
            return
        
        if RICH_AVAILABLE:
            table = create_table("Knowledge Entries", [
                "Title", "Category", "Source Agent", "Version", "Access Level", "Usage"
            ])
            
            for entry in results:
                table.add_row(
                    entry.get('title', 'Unknown')[:30],
                    entry.get('category', 'Unknown'),
                    entry.get('source_agent', 'Unknown'),
                    str(entry.get('version', 1)),
                    entry.get('access_level', 'public'),
                    str(entry.get('usage_count', 0))
                )
            
            console.print(table)
        else:
            for entry in results:
                print(f"- {entry.get('title', 'Unknown')} ({entry.get('category', 'Unknown')})")
                
    except Exception as e:
        rich_print(f"❌ Error listing knowledge: {e}", "red")


@agent_group.command()
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'summary']), 
              default='summary', help='Output format')
def system(format: str):
    """Show multi-agent system status."""
    rich_print("🖥️  Multi-Agent System Status", "bold blue")
    
    try:
        agent_manager = get_agent_manager()
        memory_manager = get_memory_manager()
        shared_kb = get_shared_knowledge()
        
        if not agent_manager:
            rich_print("❌ Agent manager not initialized", "red")
            return
        
        # Get system statistics
        agents = agent_manager.list_agents()
        isolation_report = memory_manager.get_isolation_report() if memory_manager else {}
        kb_stats = shared_kb.get_statistics() if shared_kb else {}
        
        if RICH_AVAILABLE:
            # System overview panel
            overview = Panel.fit(
                f"[bold]System Overview[/bold]\n\n"
                f"Active Agents: {len(agents)}\n"
                f"Total Memory: {isolation_report.get('total_memory_mb', 0):.1f} MB\n"
                f"Knowledge Entries: {kb_stats.get('total_entries', 0)}\n"
                f"24h Access Count: {kb_stats.get('access_count_24h', 0)}",
                title="Multi-Agent System",
                border_style="blue"
            )
            console.print(overview)
            
            # Agent summary table
            if agents:
                agent_table = create_table("Agent Summary", [
                    "Agent ID", "Status", "Memory (MB)", "Tasks", "Last Active"
                ])
                
                for agent_id in agents:
                    info = agent_manager.get_agent_info(agent_id)
                    memory_stats = agent_manager.get_agent_memory_stats(agent_id)
                    
                    agent_table.add_row(
                        agent_id,
                        info.get('status', 'Unknown'),
                        f"{memory_stats.get('memory_size_mb', 0):.1f}" if memory_stats else "0.0",
                        str(info.get('task_count', 0)),
                        info.get('last_active', 'Never')
                    )
                
                console.print(agent_table)
        else:
            print(f"Active Agents: {len(agents)}")
            print(f"Total Memory: {isolation_report.get('total_memory_mb', 0):.1f} MB")
            print(f"Knowledge Entries: {kb_stats.get('total_entries', 0)}")
            
    except Exception as e:
        rich_print(f"❌ Error getting system status: {e}", "red")


@agent_group.command()
@click.option('--agents', '-a', is_flag=True, help='Cleanup agent data')
@click.option('--memory', '-m', is_flag=True, help='Cleanup memory data')
@click.option('--knowledge', '-k', is_flag=True, help='Cleanup knowledge data')
@click.option('--all', '-A', is_flag=True, help='Cleanup all data')
@click.option('--force', '-f', is_flag=True, help='Force cleanup without confirmation')
def cleanup(agents: bool, memory: bool, knowledge: bool, all: bool, force: bool):
    """Cleanup multi-agent system data."""
    if all:
        agents = memory = knowledge = True
    
    if not any([agents, memory, knowledge]):
        rich_print("❌ Specify what to cleanup with --agents, --memory, --knowledge, or --all", "red")
        return
    
    if not force:
        items = []
        if agents: items.append("agents")
        if memory: items.append("memory")
        if knowledge: items.append("knowledge")
        
        confirmation = click.confirm(f"This will cleanup {', '.join(items)} data. Continue?")
        if not confirmation:
            rich_print("Cleanup cancelled", "yellow")
            return
    
    rich_print("🧹 Cleaning up multi-agent system", "bold blue")
    
    try:
        if agents:
            agent_manager = get_agent_manager()
            if agent_manager:
                agent_manager.shutdown()
                rich_print("✅ Agent data cleaned up", "green")
        
        if memory:
            memory_manager = get_memory_manager()
            if memory_manager:
                memory_manager.shutdown()
                rich_print("✅ Memory data cleaned up", "green")
        
        if knowledge:
            shared_kb = get_shared_knowledge()
            if shared_kb:
                shared_kb.cleanup()
                rich_print("✅ Knowledge data cleaned up", "green")
        
        rich_print("✅ Cleanup completed successfully", "green")
        
    except Exception as e:
        rich_print(f"❌ Error during cleanup: {e}", "red")


if __name__ == '__main__':
    agent_group()