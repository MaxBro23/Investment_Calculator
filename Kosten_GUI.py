import sys
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import tkinter as tk
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QFormLayout, QMessageBox
)

class FormattedLineEdit(QLineEdit):
    """Control the formatting for the user input.
    Format an input of 10000 to 10,000.00
    Furthermore, if the user clicks into a field and, therefore, puts the focus
    into this field, the formatting takes place e.g.:
    focus in field: 10,000.00 --> 100000
    focus out of field: 100000 --> 10,0000.00
    """

    def focusOutEvent(self, event):
        text = self.text().replace(',', '')
        if text:
            try:
                value = float(text)
                self.setText(f"{value:,.2f}")
            except ValueError:
                self.setText(text)
        super().focusOutEvent(event)

    def focusInEvent(self, event):
        self.setText(self.text().replace(',', ''))
        super().focusInEvent(event)

class InvestmentCalculator(QWidget):

    def __init__(self):

        # Get Screensize
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.destroy()
        self.fig_width = screen_width * 0.8 / 100  # 50% Screensize
        self.fig_height = screen_height * 0.7 / 100  # 30% Screensize
        self.font_size = screen_height * 0.01  # fontsize 1%
        self.font_size_heading = screen_height * 0.012
        app.exit()

        super().__init__()
        self.initUI()

    def initUI(self):
        """Initialise GUI"""
        self.setWindowTitle('Investment Calculator')

        layout = QFormLayout()

        # Define input fields for gui
        self.capital_input = FormattedLineEdit()
        self.rate_input = FormattedLineEdit()
        self.years_input = QLineEdit()
        self.interest_input = FormattedLineEdit()

        # Add description text to fields
        layout.addRow('Initial capital (€):', self.capital_input)
        layout.addRow('Monthly savings (€):', self.rate_input)
        layout.addRow('Period of investing (Years):', self.years_input)
        layout.addRow('Interest rate per year (%):', self.interest_input)

        # Add "Calculate"-Button
        self.calculate_button = QPushButton('Calculate')
        self.calculate_button.clicked.connect(self.calculate)

        layout.addWidget(self.calculate_button)

        self.result_label = QLabel('Resulting sum: ')
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def calculate(self):
        
        try:
            # Get input data
            initial_capital = self.parse_input(self.capital_input.text())
            monthly_rate = self.parse_input(self.rate_input.text())
            years = int(self.years_input.text())  # years as integer
            annual_interest = self.parse_input(self.interest_input.text())
            
            # Catch user input error
            if monthly_rate < 0:
                error_idx_1 = True
                raise ValueError("Monthly rate negative")
            
            # Start calculation
            capital_without_interest_rate = [initial_capital]

            total_investment = initial_capital
            total_interest_earned = 0

            own_capital = [initial_capital]
            gained_interest = [0]

            # Calc final capital with interest rate
            final_sum = initial_capital
            capital_over_time = [initial_capital]

            for i in range(1, years + 1):
                # Data for 1st investment growth plot
                final_sum = (final_sum + monthly_rate * 12) * (1 + annual_interest / 100)
                capital_without_interest_rate.append(capital_without_interest_rate[-1]+monthly_rate * 12)
                capital_over_time.append(final_sum)
                # Data for 2nd investment vs interest plot
                total_investment += monthly_rate * 12
                # Data for 3rd stacked bar chart
                own_capital.append(own_capital[-1] + monthly_rate*12)
                gained_interest.append(final_sum-total_investment)

            total_interest_earned = final_sum - total_investment

            self.result_label.setText(f'Final Sum: {final_sum:,.2f} €')

            # Show plots
            self.plot_stacked_barchart(own_capital, gained_interest)
            self.plot_investment_vs_interest(total_investment, total_interest_earned)
            self.plot_investment_growth(capital_over_time, years, capital_without_interest_rate)

        except:
            if error_idx_1:
                QMessageBox.warning(self, 'ERROR', 'Monthly rate cant be negative!')

    def parse_input(self, input_text):
        try:
            input_text = input_text.replace(',', '')
            return float(input_text)
        except ValueError:
            raise ValueError('Invalid entry!')

    def plot_investment_growth(self, capital_over_time, years, capital_without_interest_rate):
        # format function
        def format_number(value):
            return '{:,}'.format(int(value))

        # Define spacing for x-axis based on years
        if years <= 35:
            x_step = 1
        elif years > 35 and years <= 59:
            x_step = 2
        else:
            x_step = 4

        x_values = np.arange(0, len(capital_over_time), x_step)
        
        if x_values[-1] != years:
            x_values = np.append(x_values, years)
            capital_over_time = np.append(capital_over_time[::x_step], capital_over_time[-1])
        else:
            capital_over_time = capital_over_time[::x_step]
            capital_without_interest_rate = capital_without_interest_rate[::x_step]

        # Plot 
        plt.figure(figsize=(self.fig_width, self.fig_height))
        plt.plot(x_values, capital_over_time, marker='o', color="forestgreen", label="Wealth with interest rate")
        plt.plot(x_values, capital_without_interest_rate, marker='o', color="orange", label="Wealth without interest rate")
        plt.xticks(np.arange(0, years + 1, x_step), fontsize=self.font_size)
        plt.yticks(np.linspace(capital_over_time[0], capital_over_time[-1], num=10), fontsize=self.font_size)

        for i, (x, y) in enumerate(zip(x_values, capital_over_time)):
            plt.annotate(format_number(round(y, 2)), (x, y), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=self.font_size)

        for i, (x, y) in enumerate(zip(x_values, capital_without_interest_rate)):
            plt.annotate(format_number(round(y, 2)), (x, y), textcoords="offset points", xytext=(0, -20), ha='center', fontsize=self.font_size)

        # Format y-axis
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda value, _: format_number(value)))
        plt.title('Wealth over time', fontsize=self.font_size_heading)
        plt.xlabel('Years', fontsize=self.font_size_heading)
        plt.ylabel('Wealth (€)', fontsize=self.font_size_heading)
        plt.grid(True)
        plt.legend(fontsize=self.font_size)
        plt.show()

    def plot_investment_vs_interest(self, total_investment, total_interest_earned):
        # format function
        def format_func(value, tick_number):
            return '{:,}'.format(int(value))

        plt.figure(figsize=(self.fig_width, self.fig_height))
        categories = ['Invested capital', 'Earned interest', 'Total sum']
        values = [total_investment, total_interest_earned, total_investment+total_interest_earned]
        plt.bar(categories, values, color=['orange', 'forestgreen', 'navy'])
        plt.title('Invested capital vs. Earned interest', fontsize=self.font_size_heading)
        plt.ylabel('Sum (€)', fontsize=self.font_size_heading)
        for i, v in enumerate(values):
            plt.text(i, v + 0.01 * v, f"{v:,.2f} €", ha='center', va='bottom', fontsize=self.font_size)
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_func))
        plt.xticks(fontsize=self.font_size)
        plt.yticks(fontsize=self.font_size)
        plt.show()

    def plot_stacked_barchart(self, yearly_investment, yearly_interest):
        # Format function
        def format_func(value, tick_number):
            return '{:,}'.format(int(value))

        plt.figure(figsize=(self.fig_width, self.fig_height))
        index = np.arange(len(yearly_investment))

        plt.bar(index, yearly_investment, label='Invested capital', color='forestgreen')
        for i, v in enumerate(yearly_interest):
            plt.text(i, yearly_interest[i]+yearly_investment[i] + 0.01 * v, f"{v:,.0f} €\n{yearly_investment[i]:,.0f} €", ha='center', va='bottom', fontsize=self.font_size)
        plt.bar(index, yearly_interest, bottom=yearly_investment, label='Interest rate', color='orange')

        plt.xlabel('Years',fontsize=self.font_size_heading)
        plt.ylabel('Sum (€)', fontsize=self.font_size_heading)
        plt.title('Invested capital and interest rate per year', fontsize=self.font_size_heading, pad=20)
        plt.xticks(index, range(1, len(yearly_investment) + 1), fontsize=self.font_size)
        plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_func))
        plt.xticks(fontsize=self.font_size)
        plt.yticks(fontsize=self.font_size)
        # Change order in legend
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(handles[::-1], labels[::-1], fontsize=self.font_size, loc="upper left")
        # Adjust grey border around the plot
        plt.ylim(top=plt.ylim()[1] * 1.05)
        plt.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = InvestmentCalculator()
    ex.show()
    sys.exit(app.exec_())
