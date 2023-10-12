document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for the count selections function
    const allSelects = document.querySelectorAll('select');
    allSelects.forEach(select => {
        select.addEventListener('change', () => countSelections(allSelects));
    });
    // Add event listener for the form submit function
    const predForm = document.getElementById('predictions_form');
    predForm.addEventListener('submit', validateForm);
});

function countSelections(allSelects) {
    // Select all manager names
    const allManagers = document.querySelectorAll('[data-manager]');
    // Set all texts to plain text (no strong)
    allManagers.forEach(managerName => {
        managerName.innerHTML = managerName.textContent;
    });
    // Get elements where the count will be displayed
    const count1 = document.getElementById('current_selections1');
    const count2 = document.getElementById('current_selections2');
    // Set counter
    let newCount = 0;
    // Loop all select fields
    allSelects.forEach(select => {
        // Get manager id value
        let managerId = select.value.split('/')[0];
        // Add to the count and set text to strong if the manager is selected
        if (select.value !== 'not picked') {
            newCount += 1;
            const manager = document.querySelector(`[data-manager='${managerId}']`);
            const text = manager.textContent;
            manager.innerHTML = `<strong>${text}</strong>`;
        };
    });
    // Set all the count elements to the new count
    count1.innerHTML = count2.innerHTML = newCount;
    // Alert more than 30 have been selected
    if (newCount > 30) {
        alert("You have more than 30 managers selected");
    };
};

function validateForm(event) {
    // Set counter
    count = 0;
    const allSelects = document.querySelectorAll('select');
    // Loop through selected values
    allSelects.forEach(select => {
        if (select.value !== 'not picked') {
            count += 1;
        };
    });
    // Is count is 0 or higher than 30, do not let the form send
    if (count === 0) {
        alert("You can't submit an empty selection");
        event.preventDefault();
    } else if (count > 30){
        alert("The maximum number of predictions is 30");
        event.preventDefault();
    };
};