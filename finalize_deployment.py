#!/usr/bin/env python3
"""
Finalize production deployment by replacing old files with updated versions.
This script should be run once to complete the migration.
"""

import os
import shutil
from pathlib import Path

def main():
    base_dir = Path("/Users/soumyadarshandash/debate ai")
    arena_dir = base_dir / "trillm_arena"
    
    print("🚀 Finalizing Production Deployment")
    print("=" * 50)
    
    # File replacements
    replacements = [
        ("llm_updated.py", "llm.py"),
        ("debate_engine_updated.py", "debate_engine.py"),
        ("api_updated.py", "api.py"),
        ("app_updated.py", "app.py"),
    ]
    
    for old_name, new_name in replacements:
        old_path = arena_dir / old_name
        new_path = arena_dir / new_name
        
        if old_path.exists():
            print(f"📝 Updating {new_name}...")
            
            # Backup old file
            if new_path.exists():
                backup_path = arena_dir / f"{new_name}.backup"
                shutil.copy2(new_path, backup_path)
                print(f"   ✓ Backed up to {new_name}.backup")
            
            # Replace with new version
            shutil.move(str(old_path), str(new_path))
            print(f"   ✓ {new_name} updated successfully")
        else:
            print(f"   ⚠ {old_name} not found, skipping...")
    
    # Clean up old files
    print("\n🧹 Cleaning up temporary files...")
    files_to_remove = ["update_files.py", "a"]
    
    for filename in files_to_remove:
        filepath = arena_dir / filename
        if filepath.exists():
            os.remove(filepath)
            print(f"   ✓ Removed {filename}")
    
    # Check for __init__.py
    init_file = arena_dir / "__init__.py"
    if not init_file.exists():
        print("\n📦 Creating __init__.py...")
        init_file.write_text('''"""TriLLM Arena - Production-grade multi-LLM debate engine."""

__version__ = "1.0.0"
__author__ = "TriLLM Team"

from .debate_engine import run_debate_fast, DebateError

__all__ = ["run_debate_fast", "DebateError"]
''')
        print("   ✓ __init__.py created")
    
    print("\n" + "=" * 50)
    print("✅ Production Deployment Finalized!")
    print("\n📚 Next Steps:")
    print("1. Review README.md for deployment instructions")
    print("2. Copy .env.example to .env and customize if needed")
    print("3. Run: docker-compose up -d")
    print("4. Access UI at: http://localhost:8501")
    print("5. Access API at: http://localhost:8000/api/docs")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
