export class GoalCalculator {
    constructor(currentBalance) {
        this.currentBalance = currentBalance;
    }

    calculatePlan(itemName, itemPrice, emergencyFunds, targetDate) {
        const today = new Date();
        const target = new Date(targetDate);
        const daysUntilTarget = Math.ceil((target - today) / (1000 * 60 * 60 * 24));

        if (daysUntilTarget <= 0) {
            return {
                success: false,
                message: "Please select a future date"
            };
        }

        const totalNeeded = parseFloat(itemPrice) + parseFloat(emergencyFunds);
        const canBuyNow = this.currentBalance >= totalNeeded;
        const remainingToSave = totalNeeded - this.currentBalance;
        const dailySavingsNeeded = remainingToSave / daysUntilTarget;

        // If we have more than enough money, progress should be 100%
        const progress = this.currentBalance >= totalNeeded ? 100 : (this.currentBalance / totalNeeded) * 100;

        return {
            success: true,
            canBuyNow,
            remainingToSave: Math.max(0, remainingToSave),
            dailySavingsNeeded,
            daysUntilTarget,
            progress
        };
    }
}

export async function deleteGoal(goalId) {
    try {
        const confirmed = confirm("Are you sure you want to delete this goal?");
        if (!confirmed) return;

        const deleted = await eel.delete_goal(goalId)();
        if (deleted) {
            await populateGoalsTable();
        } else {
            alert("Failed to delete goal. Please try again.");
        }
    } catch (error) {
        console.error("Error deleting goal:", error);
        alert("An error occurred while deleting the goal.");
    }
}

export async function editGoal(goalId, newName, additionalField1, additionalField2) {
    try {
        const success = await eel.edit_goal(goalId, newName, additionalField1, additionalField2)();
        if (success) {
            return true;
        } else {
            alert("Failed to edit goal. Please try again.");
            return false;
        }
    } catch (error) {
        console.error("Error editing goal:", error);
        alert("An error occurred while editing the goal.");
        return false;
    }
}

window.deleteGoal = deleteGoal;
window.editGoal = editGoal;

export async function populateGoalsTable() {
    const tableBody = document.getElementById('goalsTableBody');
    if (!tableBody) return;

    const goals = await eel.get_goals()();
    const transactions = await eel.get_account_transactions(100, 0)();
    const currentBalance = transactions.reduce((balance, transaction) => {
        const amount = parseFloat(transaction[2]);
        const type = transaction[1];
        return type === 'Deposit' ? balance + amount : balance - amount;
    }, 0);
    
    console.log('Current Balance:', currentBalance);

    tableBody.innerHTML = '';

    if (!goals || goals.length === 0) {
        const row = document.createElement('tr');
        const cell = document.createElement('td');
        cell.colSpan = 8;
        cell.textContent = 'No goals found';
        cell.style.textAlign = 'center';
        row.appendChild(cell);
        tableBody.appendChild(row);
        return;
    }

    // Sort goals by date (earliest first)
    const sortedGoals = [...goals].sort((a, b) => {
        const dateA = new Date(a[4]); // dueDate is at index 4
        const dateB = new Date(b[4]);
        return dateA - dateB;
    });

    // Get monthly averages once for all goals
    const monthlyAverages = await eel.get_monthly_averages()();
    console.log('Monthly Averages:', monthlyAverages);
    const dailyNetIncome = monthlyAverages.avg_net / 30;

    for (const goal of sortedGoals) {
        const [goalId, name, targetAmount, emergencyFunds, dueDate] = goal;
        const row = document.createElement('tr');

        const totalNeeded = parseFloat(targetAmount) + parseFloat(emergencyFunds);
        console.log(`Goal ${name}:`, {
            currentBalance,
            targetAmount: parseFloat(targetAmount),
            emergencyFunds: parseFloat(emergencyFunds),
            totalNeeded
        });
        
        // Calculate days until target and adjust date
        const today = new Date();
        const targetDate = new Date(dueDate);
        targetDate.setDate(targetDate.getDate() + 1); // Add one day to fix the off-by-one issue
        const daysUntilTarget = Math.max(1, Math.ceil((targetDate - today) / (1000 * 60 * 60 * 24)));
        
        // Calculate daily savings needed
        const remainingToSave = Math.max(0, totalNeeded - currentBalance);
        const dailySavingsNeeded = remainingToSave / daysUntilTarget;
        
        // Calculate progress percentage - if we have more than needed, it's 100%
        const progress = currentBalance >= totalNeeded ? 100 : (currentBalance / totalNeeded) * 100;
        console.log(`Progress for ${name}:`, {
            progress,
            comparison: `${currentBalance} >= ${totalNeeded}`
        });
        const formattedProgress = progress.toFixed(1);

        // Generate recommendation symbol
        const recommendationSymbol = dailyNetIncome >= dailySavingsNeeded ? 
            '<span style="color: green; font-size: 1.5em;">✓</span>' : 
            '<span style="color: red; font-size: 1.5em;">✗</span>';

        const cells = [
            { content: name, align: 'left' },
            { content: `$${parseFloat(targetAmount).toFixed(2)}`, align: 'left' },
            { content: `$${parseFloat(emergencyFunds).toFixed(2)}`, align: 'left' },
            { content: `$${totalNeeded.toFixed(2)}`, align: 'left' },
            { content: `$${dailySavingsNeeded.toFixed(2)}`, align: 'left' },
            { content: targetDate.toLocaleDateString(), align: 'left' },  // Use adjusted date
            { 
                content: `<div class="progress">
                    <div class="progress-bar" role="progressbar" 
                        style="width: ${formattedProgress}%" 
                        aria-valuenow="${formattedProgress}" 
                        aria-valuemin="0" 
                        aria-valuemax="100">
                        ${formattedProgress}%
                    </div>
                </div>`,
                align: 'left'
            },
            { 
                content: recommendationSymbol,
                align: 'center'
            },
            { 
                content: `<div class="action-buttons">
                    <button class="btn btn-sm btn-primary" onclick="window.location.href='goals/rename_goals.html?id=${goalId}&name=${encodeURIComponent(name)}'">Edit</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteGoal('${goalId}')">Delete</button>
                </div>`,
                align: 'left'
            }
        ];

        cells.forEach(cell => {
            const td = document.createElement('td');
            td.innerHTML = cell.content;
            td.style.textAlign = cell.align;
            row.appendChild(td);
        });

        tableBody.appendChild(row);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-goal-form');
    if (form) {
        const resultDiv = document.getElementById('calculation-result');
        const progressBar = document.querySelector('.progress');
        const progressBarInner = document.querySelector('.progress-bar');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const currentBalance = await eel.get_latest_balance()();
            const calculator = new GoalCalculator(currentBalance);

            const result = calculator.calculatePlan(
                form.goal_name.value,
                form.target_amount.value,
                form.emergency_funds.value,
                form.due_date.value
            );

            if (!result.success) {
                resultDiv.className = 'alert alert-danger';
                resultDiv.textContent = result.message;
                resultDiv.style.display = 'block';
                progressBar.style.display = 'none';
                return;
            }

            const goalAdded = await eel.add_goal(
                form.goal_name.value,
                form.target_amount.value,
                form.emergency_funds.value,
                form.due_date.value
            )();

            if (goalAdded) {
                let message = '';
                if (result.canBuyNow) {
                    message = `Goal added successfully! You can buy ${form.goal_name.value} now while maintaining your emergency fund!`;
                } else {
                    message = `Goal added successfully!\n\nTo buy ${form.goal_name.value} by the target date:\n` +
                             `• You need to save $${result.remainingToSave.toFixed(2)} more\n` +
                             `• Daily savings needed: $${result.dailySavingsNeeded.toFixed(2)}\n` +
                             `• Days until target: ${result.daysUntilTarget}`;
                }

                resultDiv.className = 'alert alert-success';
                resultDiv.textContent = message;
                
                form.reset();

                setTimeout(() => {
                    window.location.href = '../goals/index.html';
                }, 2000);
            } else {
                resultDiv.className = 'alert alert-danger';
                resultDiv.textContent = 'Error adding goal. Please try again.';
            }

            resultDiv.style.display = 'block';
            progressBar.style.display = 'block';
            progressBarInner.style.width = `${result.progress}%`;
            progressBarInner.textContent = `${Math.round(result.progress)}%`;
        });
    }
});

export async function addGoal(goalName, targetAmount, emergencyFunds, dueDate) {
    try {
        const success = await eel.add_goal(goalName, targetAmount, emergencyFunds, dueDate)();
        if (success) {
            return true;
        } else {
            alert("Failed to add goal. Please try again.");
            return false;
        }
    } catch (error) {
        console.error("Error adding goal:", error);
        alert("An error occurred while adding the goal.");
        return false;
    }
}

window.addGoal = addGoal;