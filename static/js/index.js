document.addEventListener("DOMContentLoaded", function () {
  let spoilerButtons = document.querySelectorAll(".spoiler-button");

  spoilerButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      let spoilerContent = this.nextElementSibling; // Get the next element, which is the spoiler content div
      let h5 = button.querySelector("h5");
      let buttonText = h5.textContent; // Get the text content of the button

      if (buttonText.includes("▷")) {
        // Button is in collapsed state, change to expanded
        spoilerContent.style.display = "block";
        spoilerContent.style.maxHeight = null;
        h5.textContent = buttonText.replace("▷", "▽"); // Change → to ↓
      } else {
        // Button is in expanded state, change to collapsed
        spoilerContent.style.display = "none";
        h5.textContent = buttonText.replace("▽", "▷"); // Change ↓ to →
      }
    });
  });

  let assetNameButton = document.getElementById("asset-names");
  let totalPredButton = document.getElementById("total-pred");
  let correctPredButton = document.getElementById("correct-pred");
  let incorrectPredButton = document.getElementById("incorrect-pred");
  let assets = document.querySelector('#assets');

  assetNameButton.addEventListener("click", function () {
      sortTableByClass("sortable0", assets, assetNameButton, totalPredButton, correctPredButton, incorrectPredButton);
    });

  totalPredButton.addEventListener("click", function () {
      sortTableByClass("sortable1", assets, totalPredButton, correctPredButton, incorrectPredButton, assetNameButton);
    });

  correctPredButton.addEventListener("click", function () {
      sortTableByClass("sortable2", assets, correctPredButton, totalPredButton, incorrectPredButton, assetNameButton);
    });

  incorrectPredButton.addEventListener("click", function () {
      sortTableByClass("sortable3", assets, incorrectPredButton, totalPredButton, correctPredButton, assetNameButton);
    });
  });


function sortTableByClass(className, assets, button, button2, button3, button4) {
  // Check if ▽ character is present in the text of the button
  if (button.textContent.includes("▽")) {
    // If ▽ character is present, do nothing
    return;
  }

  var trs = Array.from(assets.getElementsByTagName('tr'));

  trs.sort(function(a, b) {
    var valueA = a.querySelector('.' + className).textContent.trim();
    var valueB = b.querySelector('.' + className).textContent.trim();

    if (className !== 'sortable0') {
      // Convert values to numbers for sorting
      return parseFloat(valueB) - parseFloat(valueA);
    } else {
      // Use localeCompare for alphabetical sorting
      return valueA.localeCompare(valueB);
    };
  });

  // Clear the existing <tbody>
  assets.innerHTML = '';

  // Re-insert the sorted <tr> elements back into the <tbody>
  trs.forEach(function(tr) {
    assets.appendChild(tr);
  });

  // Add a space and ▽ character to the button text
  button.textContent = button.textContent.replace(" ▷", " ▽");
  button2.textContent = button2.textContent.replace(" ▽", " ▷");
  button3.textContent = button3.textContent.replace(" ▽", " ▷");
  button4.textContent = button4.textContent.replace(" ▽", " ▷");
};
