from app import create_app, db

app = create_app()
with app.app_context():  # Needed for db.create_all()
    db.create_all()      # Creates Order table automatically

@app.cli.command()
def initdb():
    with app.app_context():
        db.create_all()
        print("Order table created!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
