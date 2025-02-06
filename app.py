from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
db = SQLAlchemy(app)

# Models
class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Float, default=0.0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)  # deposit, withdrawal
    account = db.relationship('Account', backref=db.backref('transactions', lazy=True))

# Routes
@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.json
    new_account = Account(name=data['name'], account_type=data['account_type'])
    db.session.add(new_account)
    db.session.commit()
    return jsonify({'message': 'Account created successfully'})

@app.route('/accounts', methods=['GET'])
def get_accounts():
    accounts = Account.query.all()
    return jsonify([{'id': acc.id, 'name': acc.name, 'account_type': acc.account_type, 'balance': acc.balance} for acc in accounts])

@app.route('/create_transaction', methods=['POST'])
def create_transaction():
    data = request.json
    account = Account.query.get(data['account_id'])
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    if data['transaction_type'] == 'withdrawal' and account.balance < data['amount']:
        return jsonify({'error': 'Insufficient funds'}), 400
    account.balance += data['amount'] if data['transaction_type'] == 'deposit' else -data['amount']
    transaction = Transaction(account_id=data['account_id'], amount=data['amount'], transaction_type=data['transaction_type'])
    db.session.add(transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction successful'})

@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    return jsonify([{'id': txn.id, 'account_id': txn.account_id, 'amount': txn.amount, 'transaction_type': txn.transaction_type} for txn in transactions])

@app.route('/search_transactions', methods=['GET'])
def search_transactions():
    account_id = request.args.get('account_id')
    transactions = Transaction.query.filter_by(account_id=account_id).all()
    return jsonify([{'id': txn.id, 'account_id': txn.account_id, 'amount': txn.amount, 'transaction_type': txn.transaction_type} for txn in transactions])

@app.route('/top_customers', methods=['GET'])
def top_customers():
    top_accounts = Account.query.order_by(Account.balance.desc()).limit(5).all()
    return jsonify([{'id': acc.id, 'name': acc.name, 'balance': acc.balance} for acc in top_accounts])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
