from src.cli import build_parser
from src.storage import get_default_db_path, load

def main():
    db_path = get_default_db_path()
    db = load(db_path)
    
    parser = build_parser()
    args = parser.parse_args()
    
    # Execute the selected command, passing the DB and path
    args.fn(args, db, db_path)

if __name__ == "__main__":
    main()
