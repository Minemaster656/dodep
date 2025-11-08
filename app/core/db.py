from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from colorama import Fore, Style
from app.core.models import Base
from alembic.config import Config
from alembic import command

# Создание подключения
engine = create_engine('sqlite:///data.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
# Проверка версии через Alembic
alembic_cfg = Config("alembic.ini")

try:
    # Получить текущую версию
    from alembic.script import ScriptDirectory
    from alembic.runtime.migration import MigrationContext
    
    script = ScriptDirectory.from_config(alembic_cfg)
    with engine.begin() as conn:
        context = MigrationContext.configure(conn)
        current_rev = context.get_current_revision()
        
    if current_rev:
        print(f"{Fore.GREEN}DB SCHEMA VERSION: {Style.BRIGHT}{Fore.BLUE}{current_rev}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}No migration applied yet{Style.RESET_ALL}")
        
    # Применить все миграции автоматически
    command.upgrade(alembic_cfg, "head")
    
except Exception as e:
    print(f"{Fore.RED}Error checking migrations: {e}{Style.RESET_ALL}")
    # Создать таблицы напрямую, если миграции не настроены
    Base.metadata.create_all(engine)
