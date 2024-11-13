// static/js/auth.js

function showAlert(message, type) {
    const alertElement = document.getElementById(`${type}-alert`);
    alertElement.textContent = message;
    alertElement.style.display = 'block';
    setTimeout(() => {
        alertElement.style.display = 'none';
    }, 5000);
}

function togglePassword(id = 'password') {
    const passwordInput = document.getElementById(id);
    passwordInput.type = passwordInput.type === 'password' ? 'text' : 'password';
}

// async function handleLogin(event) {
//     event.preventDefault();
    
//     const formData = {
//         usemo: document.getElementById('usemo').value,
//         password: document.getElementById('password').value
//     };

//     try {
//         const response = await fetch('/user/login/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(formData)
//         });

//         const data = await response.json();

//         if (data.success) {
//             showAlert(data.message, 'success');
//             localStorage.setItem('token', data.data.token);
//             setTimeout(() => {
//                 window.location.href = `/fc/flashcards/?token=${data.data.token}`;
//             }, 1000);
//         } else {
//             showAlert(data.message, 'error');
//         }
//     } catch (error) {
//         showAlert('An error occurred during login. Please try again.', 'error');
//     }
// }

async function handleLogin(event) {
    event.preventDefault();
    
    const formData = {
        usemo: document.getElementById('usemo').value,
        password: document.getElementById('password').value
    };

    try {
        const response = await axios.post('/user/login/', formData);

        const data = response.data;

        if (data.success) {
            showAlert(data.message, 'success');
            localStorage.setItem('token', data.data.token);
            console.log("Token _ login:", localStorage.getItem('token'));
            // Load the flashcards content using Axios
            setTimeout(async () => {
                try {
                    const flashcardResponse = await axios.get('/fc/flashcards/');
                    document.body.innerHTML = flashcardResponse.data; // Replace the page content with the flashcards page
                } catch (flashcardError) {
                    showAlert('Failed to load flashcards. Please try again.', 'error');
                }
            }, 1000);
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        showAlert('An error occurred during login. Please try again.', 'error');
    }
}


async function handleSignup(event) {
    event.preventDefault();
    
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    if (password !== confirmPassword) {
        showAlert('Passwords do not match!', 'error');
        return;
    }

    const formData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        mobile: document.getElementById('mobile').value,
        password: password
    };
    console.log(formData);
    console.log(JSON.stringify(formData));
    
    try {
        const response = await fetch('/user/join/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            showAlert(data.message, 'success');
            localStorage.setItem('token', data.data.token);
            setTimeout(() => {
                window.location.href = '/fc/flashcards/';
            }, 1000);
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        showAlert('An error occurred during signup. Please try again.', 'error');
    }
}

async function requestOTP(event) {
    event.preventDefault();
    
    const usemo = document.getElementById('usemo').value;
    
    try {
        const response = await fetch('/user/otp/', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ usemo })
        });

        const data = await response.json();
        
        if (data.success) {
            showAlert('OTP has been sent! Please check your email/phone.', 'success');
            document.getElementById('otpForm').style.display = 'none';
            document.getElementById('resetForm').style.display = 'block';
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        showAlert('An error occurred. Please try again.', 'error');
    }
}

async function handlePasswordReset(event) {
    event.preventDefault();
    
    const password = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    if (password !== confirmPassword) {
        showAlert('Passwords do not match!', 'error');
        return;
    }

    const formData = {
        usemo: document.getElementById('usemo').value,
        otp: document.getElementById('otp').value,
        password: password
    };

    try {
        const response = await fetch('/user/password/', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            showAlert(data.message, 'success');
            setTimeout(() => {
                window.location.href = '/user/signin';
            }, 2000);
        } else {
            showAlert(data.message, 'error');
        }
    } catch (error) {
        showAlert('An error occurred. Please try again.', 'error');
    }
}