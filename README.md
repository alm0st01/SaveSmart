# SaveSmart  

## Overview  
SaveSmart is an financial tracking application designed to help users manage their income, expenses, and savings goals easily. With SaveSmart, users will be able to:  
- Create an account and securely store financial data.  
- Log transactions including purchases, withdrawals, and transfers  
- View an organized table that displays financial history by name, date, type, amount, and description.  
- Analyze spending habits with interactive graphs for income and expenses.
- Set and track set future financial goals with a budgeting system that calculates daily savings targets.
- Secure user data locally with encryption to ensure privacy.  

## Design
SaveSmart consists of a frontend and backend system:  
- Backend: Handles data storage, encryption, and financial calculations.  
- Frontend: Provides an interactive, friendly UI for users to manage their finances.  

### Calculations
Charts:
 - Stored the total number of withdrawals and deposits.
 - Divided the total number of withdrawals or deposits by the number in a certain, and sent this data to the graph.
 Goals:
  - When creating a goal, users are asked how much money they wanted to store in their account at all times, the price of the item, and the date that they wanted to get the item by.
  - If the user has enough money in their account to buy the item and still have enough for the emergency fund, they were reccomended to buy the item
  - If the user didn't have enough, we found out how much they were missing by subtracting their current balance from the goal (emergency + price).
  - Displayed amount to save each day by dividing goal by the number of days from the current date to the target date and 
  - Dispayed percentage by dividing goal amount from current amount

### Data Storage
- Transactions, user accounts, and goals are stored securely with encryption.  
- Data validation: Input fields prevent invalid data from being entered. 

### Permissions
- Users only have access to their own financial data.  
- A message is displayed if users try to access pages that they are not supposed to have access to by copying links 