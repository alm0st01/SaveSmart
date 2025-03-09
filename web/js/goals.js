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
        const canBuyNow = this.currentBalance - itemPrice > emergencyFunds;
        const remainingToSave = totalNeeded - this.currentBalance;
        const dailySavingsNeeded = remainingToSave / daysUntilTarget;

        const progress = (this.currentBalance / totalNeeded) * 100;

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

// Form handling
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-goal-form');
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

        let message = '';
        if (result.canBuyNow) {
            message = `You can buy ${form.goal_name.value} now while maintaining your emergency fund!`;
        } else {
            message = `To buy ${form.goal_name.value} by the target date:\n` +
                     `• You need to save $${result.remainingToSave.toFixed(2)} more\n` +
                     `• Daily savings needed: $${result.dailySavingsNeeded.toFixed(2)}\n` +
                     `• Days until target: ${result.daysUntilTarget}`;
        }

        resultDiv.className = 'alert alert-info';
        resultDiv.textContent = message;
        resultDiv.style.display = 'block';

        progressBar.style.display = 'block';
        progressBarInner.style.width = `${result.progress}%`;
        progressBarInner.textContent = `${Math.round(result.progress)}%`;
    });
});