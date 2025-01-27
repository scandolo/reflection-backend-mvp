document.addEventListener('DOMContentLoaded', function() {
  const userInput = document.getElementById('userInput');
  const reflectButton = document.getElementById('reflectButton');
  const questionArea = document.getElementById('questionArea');
  const generatedQuestion = document.getElementById('generatedQuestion');

  reflectButton.addEventListener('click', async function() {
      const text = userInput.value.trim();

      if (!text) {
          alert('Please share your thoughts first.');
          return;
      }

      try {
          reflectButton.disabled = true;
          reflectButton.textContent = 'reflecting...';

          const response = await fetch('/generate_question', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify({ text: text })
          });

          const data = await response.json();

          if (data.success) {
              questionArea.classList.remove('hidden');
              generatedQuestion.textContent = data.question;

              // Trigger animation
              setTimeout(() => {
                  questionArea.classList.add('visible');
              }, 10);

              // Clear input and prepare for next reflection
              userInput.value = '';
              userInput.placeholder = 'Reflect on the question above...';
          } else {
              throw new Error(data.error || 'Failed to generate question');
          }
      } catch (error) {
          alert('An error occurred. Please try again.');
          console.error('Error:', error);
      } finally {
          reflectButton.disabled = false;
          reflectButton.textContent = 'help me reflect';
      }
  });
});
