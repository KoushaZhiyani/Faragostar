class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance  # ویژگی خصوصی (private)

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            print(f"مبلغ {amount} واریز شد. موجودی: {self.__balance}")
        else:
            print("مبلغ واریز باید مثبت باشد.")

    def withdraw(self, amount):
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            print(f"مبلغ {amount} برداشت شد. موجودی: {self.__balance}")
        else:
            print("موجودی ناکافی یا مبلغ نامعتبر.")

    def get_balance(self):
        return self.__balance

# استفاده
acc = Account("علی", 1000)
acc.deposit(500)          # مبلغ 500 واریز شد. موجودی: 1500
acc.withdraw(200)         # مبلغ 200 برداشت شد. موجودی: 1300
# print(acc.__balance)    # خطا! خصوصی است
print(acc.get_balance())  # 1300