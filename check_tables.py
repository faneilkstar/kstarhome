from dotenv import load_dotenv
load_dotenv()
from app import create_app, db
app = create_app()
with app.app_context():
    r = db.session.execute(db.text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"))
    tables = [x[0] for x in r.fetchall()]
    print("TABLES:", tables)

    r2 = db.session.execute(db.text("SELECT column_name FROM information_schema.columns WHERE table_name='enseignants' ORDER BY ordinal_position"))
    print("ENSEIGNANTS:", [x[0] for x in r2.fetchall()])

