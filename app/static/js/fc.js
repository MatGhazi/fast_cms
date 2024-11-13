console.log('fc.js is loading...');

// handleAdd function in your main script
console.log("fc start");
async function handleAdd(event) {
    event.preventDefault();
    
    const formData = {
        question: document.getElementById('new-question').value,
        answer: document.getElementById('new-answer').value
    };

    try {
        // Make the request with Axios
        console.log("Token _ fc:", localStorage.getItem('token'));
        const response = await axios.post('/fc/add_flashcard', formData);

        if (response.data.success) {
            window.location.reload();
        } else {
            showAlert(response.data.message, 'error');
        }
    } catch (error) {
        showAlert('Error adding flashcard', 'error');
    }
}


// // Check for authentication
// function checkAuth() {
//     const token = localStorage.getItem('token');
//     if (!token) {
//         window.location.href = '/user/login';
//         return false;
//     }
//     return token;
// }

// // Common fetch with auth headers
// async function authenticatedFetch(url, options = {}) {
//     const token = checkAuth();
//     if (!token) return;

//     const defaultHeaders = {
//         'Authorization': `Bearer ${token}`,
//         'Content-Type': 'application/json',
//     };

//     const response = await fetch(url, {
//         ...options,
//         headers: {
//             ...defaultHeaders,
//             ...options.headers
//         }
//     });

//     if (response.status === 401) {
//         localStorage.removeItem('token');
//         window.location.href = '/user/login';
//         return;
//     }

//     return response;
// }

// function showAlert(message, type) {
//     // Implement your alert function here
//     alert(message);
// }

// function showAnswer() {
//     document.getElementById('answer').style.display = 'block';
// }

// function showEditForm() {
//     document.getElementById('edit-form').style.display = 'block';
// }

// async function handleAnswer(event, flashcardId) {
//     event.preventDefault();
//     const correct = event.submitter.value === 'true';
    
//     try {
//         const response = await authenticatedFetch(`/fc/answer/${flashcardId}`, {
//             method: 'POST',
//             body: JSON.stringify({ correct })
//         });

//         if (response) {
//             const data = await response.json();
//             if (data.success) {
//                 window.location.reload();
//             } else {
//                 showAlert(data.message, 'error');
//             }
//         }
//     } catch (error) {
//         showAlert('Error updating flashcard', 'error');
//     }
// }

// async function handleEdit(event, flashcardId) {
//     event.preventDefault();
//     const formData = {
//         edited_question: document.getElementById('edited-question').value,
//         edited_answer: document.getElementById('edited-answer').value
//     };

//     try {
//         const response = await authenticatedFetch(`/fc/edit_flashcard/${flashcardId}`, {
//             method: 'POST',
//             body: JSON.stringify(formData)
//         });

//         if (response) {
//             const data = await response.json();
//             if (data.success) {
//                 window.location.reload();
//             } else {
//                 showAlert(data.message, 'error');
//             }
//         }
//     } catch (error) {
//         showAlert('Error editing flashcard', 'error');
//     }
// }

// async function handleDelete(flashcardId) {
//     if (confirm('Are you sure you want to delete this flashcard?')) {
//         try {
//             const response = await authenticatedFetch(`/fc/delete_flashcard/${flashcardId}`, {
//                 method: 'POST'
//             });

//             if (response) {
//                 const data = await response.json();
//                 if (data.success) {
//                     window.location.reload();
//                 } else {
//                     showAlert(data.message, 'error');
//                 }
//             }
//         } catch (error) {
//             showAlert('Error deleting flashcard', 'error');
//         }
//     }
// }

// // async function handleAdd(event) {
// //     event.preventDefault();
// //     const formData = {
// //         question: document.getElementById('new-question').value,
// //         answer: document.getElementById('new-answer').value
// //     };

// //     try {
// //         const response = await authenticatedFetch('/fc/add_flashcard', {
// //             method: 'POST',
// //             body: JSON.stringify(formData)
// //         });

// //         if (response) {
// //             const data = await response.json();
// //             if (data.success) {
// //                 window.location.reload();
// //             } else {
// //                 showAlert(data.message, 'error');
// //             }
// //         }
// //     } catch (error) {
// //         showAlert('Error adding flashcard', 'error');
// //     }
// // }




// async function generateAnswer() {
//     const question = document.getElementById('new-question').value;
    
//     try {
//         const response = await authenticatedFetch('/fc/generate_answer', {
//             method: 'POST',
//             body: JSON.stringify({ question })
//         });

//         if (response) {
//             const data = await response.json();
//             document.getElementById('new-answer').value = data.answer;
//         }
//     } catch (error) {
//         showAlert('Error generating answer', 'error');
//     }
// }

// async function generateStory() {
//     try {
//         const response = await authenticatedFetch('/fc/generate_story', {
//             method: 'POST'
//         });

//         if (response) {
//             const data = await response.json();
//             const storyContainer = document.getElementById('story-container');
//             storyContainer.innerHTML = `<h3>Story</h3><p>${data.story}</p>`;
            
//             const audioElement = document.createElement("audio");
//             audioElement.src = data.audio_path;
//             audioElement.controls = true;
//             storyContainer.appendChild(audioElement);
//         }
//     } catch (error) {
//         showAlert('Error generating story', 'error');
//     }
// }

// // Check authentication when page loads
// document.addEventListener('DOMContentLoaded', checkAuth);