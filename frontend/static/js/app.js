// Helper function to display responses in a formatted way
function displayResponse(elementId, data) {
    const outputElement = document.getElementById(elementId);
    if (!data) {
        outputElement.innerHTML = '<p style="color: red;">No data received or an error occurred.</p>';
        return;
    }

    let htmlContent = '<div>';

    // Handle generic fields first
    if (data.id) htmlContent += `<p><strong>ID:</strong> ${data.id}</p>`;
    if (data.citizen_id) htmlContent += `<p><strong>Citizen ID:</strong> ${data.citizen_id}</p>`;
    if (data.filename) htmlContent += `<p><strong>Filename:</strong> ${data.filename}</p>`;
    if (data.description) htmlContent += `<p><strong>Description:</strong> ${data.description}</p>`;
    if (data.language) htmlContent += `<p><strong>Language:</strong> ${data.language}</p>`;
    if (data.category) htmlContent += `<p><strong>Category:</strong> <span style="color: #0056b3; font-weight: bold;">${data.category}</span></p>`;
    if (data.urgency_score !== undefined) {
        let scoreColor = 'green';
        if (data.urgency_score >= 80) scoreColor = 'red';
        else if (data.urgency_score >= 50) scoreColor = 'orange';
        htmlContent += `<p><strong>Urgency Score:</strong> <span style="color: ${scoreColor}; font-weight: bold;">${data.urgency_score}</span> / 100</p>`;
    }
    if (data.department) htmlContent += `<p><strong>Department:</strong> ${data.department}</p>`;
    if (data.estimated_cost !== undefined) htmlContent += `<p><strong>Estimated Cost:</strong> ₹${data.estimated_cost.toLocaleString()}</p>`;
    
    // Handle list-like fields
    const listFields = [
        { key: 'required_resources', label: 'Required Resources' },
        { key: 'suggested_actions', label: 'Suggested Actions' },
        { key: 'tools_required', label: 'Tools Required' },
        { key: 'safety_notes', label: 'Safety Notes', color: '#d32f2f' },
    ];

    listFields.forEach(field => {
        if (data[field.key] && Array.isArray(data[field.key]) && data[field.key].length > 0) {
            htmlContent += `<p><strong>${field.label}:</strong></p><ul>`;
            data[field.key].forEach(item => {
                htmlContent += `<li style="color: ${field.color || 'inherit'};">${item}</li>`;
            });
            htmlContent += `</ul>`;
        }
    });

    if (data.sla_hours !== undefined) htmlContent += `<p><strong>SLA (Hours):</strong> ${data.sla_hours}</p>`;
    if (data.status) htmlContent += `<p><strong>Status:</strong> <span style="color: #28a745; font-weight: bold;">${data.status.charAt(0).toUpperCase() + data.status.slice(1)}</span></p>`;
    if (data.created_at) htmlContent += `<p><strong>Created At:</strong> ${new Date(data.created_at).toLocaleString()}</p>`;

    // Circular specific fields
    if (data.content_summary) htmlContent += `<p><strong>Circular Summary:</strong> ${data.content_summary}</p>`;
    if (data.extracted_rules && Array.isArray(data.extracted_rules) && data.extracted_rules.length > 0) {
        htmlContent += `<p><strong>Extracted Rules:</strong></p><ul>`;
        data.extracted_rules.forEach(rule => {
            htmlContent += `<li><strong>${rule.rule_text}</strong>`;
            if (rule.keywords && Array.isArray(rule.keywords) && rule.keywords.length > 0) {
                htmlContent += ` (Keywords: ${rule.keywords.join(', ')})`;
            }
            htmlContent += `</li>`;
        });
        htmlContent += `</ul>`;
    }
    if (data.eligibility_criteria) htmlContent += `<p><strong>Eligibility Criteria:</strong> ${data.eligibility_criteria}</p>`;
    if (data.deadlines) htmlContent += `<p><strong>Deadlines:</strong> ${data.deadlines}</p>`;
    if (data.uploaded_at) htmlContent += `<p><strong>Uploaded At:</strong> ${new Date(data.uploaded_at).toLocaleString()}</p>`;

    htmlContent += '</div>';
    outputElement.innerHTML = htmlContent;
}

// Global state for authentication
let currentUser = null;
let accessToken = null;

// Function to decode JWT token
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

// Function to update UI based on login status and role
function updateUI() {
    const token = localStorage.getItem('accessToken');
    const isLoggedIn = !!token; // Convert token presence to a boolean

    // Get all sections and forms that need to be controlled
    const authSection = document.getElementById('auth-section');
    const complaintSubmissionSection = document.getElementById('complaint-submission-section');
    const pdfUploadSection = document.getElementById('pdf-upload-section');
    const documentGenerationSection = document.getElementById('document-generation-section');
    const statusTrackingSection = document.getElementById('status-tracking-section');
    const sortedComplaintsSection = document.getElementById('sorted-complaints-section'); // New: Get sorted complaints section

    const loginNav = document.getElementById('nav-login');
    const registerNav = document.getElementById('nav-register');
    const logoutNavLi = document.getElementById('nav-logout-li');

    // Individual forms within document generation
    const rtiForm = document.getElementById('rtiForm');
    const schemeAppForm = document.getElementById('schemeAppForm');
    const noticeForm = document.getElementById('noticeForm');
    const workOrderForm = document.getElementById('workOrderForm');

    // Hide all by default
    [authSection, complaintSubmissionSection, pdfUploadSection, documentGenerationSection, statusTrackingSection, sortedComplaintsSection].forEach(el => {
        if (el) el.style.display = 'none';
    });
    
    // Hide all document generation forms by default
    [rtiForm, schemeAppForm, noticeForm, workOrderForm].forEach(el => {
        if (el) el.style.display = 'none';
    });

    if (isLoggedIn) {
        const decodedToken = parseJwt(token);
        currentUser = { email: decodedToken.sub, role: decodedToken.role };
        accessToken = token;

        loginNav.style.display = 'none';
        registerNav.style.display = 'none';
        logoutNavLi.style.display = 'block';

        let docGenSectionVisible = false; // Flag to check if any doc gen form is visible

        if (currentUser.role === 'citizen') {
            complaintSubmissionSection.style.display = 'block';
            statusTrackingSection.style.display = 'block';
            if (rtiForm) rtiForm.style.display = 'block';
            if (schemeAppForm) schemeAppForm.style.display = 'block';
            if (rtiForm || schemeAppForm) docGenSectionVisible = true;
        } else if (currentUser.role === 'department_admin') {
            pdfUploadSection.style.display = 'block';
            if (noticeForm) noticeForm.style.display = 'block';
            if (workOrderForm) workOrderForm.style.display = 'block';
            if (noticeForm || workOrderForm) docGenSectionVisible = true;
            statusTrackingSection.style.display = 'block'; // Admins can also track status
            sortedComplaintsSection.style.display = 'block'; // Show sorted complaints for admin
            loadSortedComplaints(); // Load complaints for admin
        }

        if (docGenSectionVisible) {
            documentGenerationSection.style.display = 'block';
        }

        // Show circulars section for all logged-in users
        document.getElementById('circulars-display-section').style.display = 'block';
        loadCirculars(); // Load circulars when UI updates after login
    } else {
        currentUser = null;
        accessToken = null;

        loginNav.style.display = 'block';
        registerNav.style.display = 'block';
        logoutNavLi.style.display = 'none';

        // Hide all operational sections if not logged in
        document.getElementById('complaint-submission-section').style.display = 'none';
        document.getElementById('pdf-upload-section').style.display = 'none';
        document.getElementById('document-generation-section').style.display = 'none';
        document.getElementById('status-tracking-section').style.display = 'none';
        document.getElementById('circulars-display-section').style.display = 'none'; // Ensure circulars section is hidden
        if (sortedComplaintsSection) sortedComplaintsSection.style.display = 'none'; // Hide for non-admins
        document.getElementById('auth-section').style.display = 'block'; // Show login/register by default
        document.getElementById('login-form-container').style.display = 'block'; // Show login form
        document.getElementById('register-form-container').style.display = 'none'; // Hide register form
    }
}

// Generic fetch wrapper to include authorization header
async function authenticatedFetch(url, options = {}) {
    const headers = {
        ...options.headers,
    };
    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }
    
    const response = await fetch(url, {
        ...options,
        headers,
    });

    if (response.status === 401 || response.status === 403) {
        // Token expired or invalid, or not enough permissions
        alert('Session expired or not authorized. Please log in again.');
        localStorage.removeItem('accessToken');
        updateUI();
        throw new Error('Unauthorized or Forbidden');
    }
    return response;
}

// Function to load and display circulars
async function loadCirculars() {
    const circularsListDiv = document.getElementById('circulars-list');
    circularsListDiv.innerHTML = '<h3>Loading Circulars...</h3>';
    try {
        const response = await authenticatedFetch('/api/circulars');
        const circulars = await response.json();

        if (circulars.length === 0) {
            circularsListDiv.innerHTML = '<p>No circulars uploaded yet.</p>';
            return;
        }

        let html = '<div class="circulars-grid">';
        circulars.forEach(circular => {
            html += `
                <div class="circular-card card">
                    <h4>${circular.filename} (ID: ${circular.id})</h4>
                    <p><strong>Uploaded:</strong> ${new Date(circular.uploaded_at).toLocaleDateString()}</p>
                    ${circular.content_summary ? `<p><strong>Summary:</strong> ${circular.content_summary.substring(0, 150)}...</p>` : ''}
                    ${circular.extracted_rules && circular.extracted_rules.length > 0 ? 
                        `<p><strong>Key Rules:</strong></p><ul>` + 
                        circular.extracted_rules.map(rule => `<li>${rule.rule_text}</li>`).join('') + 
                        `</ul>`
                        : ''}
                    ${circular.eligibility_criteria ? `<p><strong>Eligibility:</strong> ${circular.eligibility_criteria.substring(0, 100)}...</p>` : ''}
                    ${circular.deadlines ? `<p><strong>Deadlines:</strong> ${circular.deadlines}</p>` : ''}
                </div>
            `;
        });
        html += '</div>';
        circularsListDiv.innerHTML = html;

    } catch (error) {
        console.error('Error loading circulars:', error);
        circularsListDiv.innerHTML = '<p style="color: red;">Failed to load circulars.</p>';
    }
}

// Function to load and display sorted complaints (for Admin)
async function loadSortedComplaints() {
    const sortedComplaintsListBody = document.querySelector('#sorted-complaints-list tbody');
    const sortedComplaintsMessage = document.getElementById('sorted-complaints-message');
    sortedComplaintsListBody.innerHTML = ''; // Clear previous results
    sortedComplaintsMessage.textContent = 'Loading prioritized complaints...';

    try {
        const response = await authenticatedFetch('/api/complaints/sorted');
        const complaints = await response.json();

        if (complaints.length === 0) {
            sortedComplaintsMessage.textContent = 'No complaints to prioritize.';
            return;
        }

        sortedComplaintsMessage.textContent = ''; // Clear loading message
        complaints.forEach(complaint => {
            const row = sortedComplaintsListBody.insertRow();
            row.innerHTML = `
                <td>${complaint.id}</td>
                <td>${complaint.urgency_score !== undefined ? complaint.urgency_score : 'N/A'}</td>
                <td>${complaint.category || 'N/A'}</td>
                <td>${complaint.department || 'N/A'}</td>
                <td>${complaint.description.substring(0, 100)}...</td>
                <td id="status-${complaint.id}">${complaint.status ? complaint.status.charAt(0).toUpperCase() + complaint.status.slice(1) : 'N/A'}</td>
                <td>${new Date(complaint.created_at).toLocaleDateString()}</td>
                <td>
                    <select class="complaint-status-select" data-complaint-id="${complaint.id}">
                        <option value="pending" ${complaint.status === 'pending' ? 'selected' : ''}>Pending</option>
                        <option value="processing" ${complaint.status === 'processing' ? 'selected' : ''}>Processing</option>
                        <option value="resolved" ${complaint.status === 'resolved' ? 'selected' : ''}>Resolved</option>
                    </select>
                </td>
            `;
        });

        // Add event listeners for status change dropdowns
        document.querySelectorAll('.complaint-status-select').forEach(selectElement => {
            selectElement.addEventListener('change', async (event) => {
                const complaintId = event.target.dataset.complaintId;
                const newStatus = event.target.value;

                try {
                    const response = await authenticatedFetch(`/api/complaints/${complaintId}/status`, {
                        method: 'PATCH',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ status: newStatus }),
                    });
                    const updatedComplaint = await response.json();

                    if (response.ok) {
                        // Update the displayed status in the table
                        document.getElementById(`status-${complaintId}`).textContent = updatedComplaint.status.charAt(0).toUpperCase() + updatedComplaint.status.slice(1);
                        alert(`Complaint ID ${complaintId} status updated to ${updatedComplaint.status}.`);
                    } else {
                        alert(`Failed to update status for Complaint ID ${complaintId}: ${updatedComplaint.detail || 'Unknown error'}`);
                        // Revert dropdown to previous state on error
                        event.target.value = complaints.find(c => c.id == complaintId).status; 
                    }
                } catch (error) {
                    console.error(`Error updating status for complaint ${complaintId}:`, error);
                    alert(`An error occurred while updating status for Complaint ID ${complaintId}.`);
                    // Revert dropdown to previous state on error
                    event.target.value = complaints.find(c => c.id == complaintId).status; 
                }
            });
        });

    } catch (error) {
        console.error('Error loading sorted complaints:', error);
        sortedComplaintsMessage.textContent = 'Failed to load prioritized complaints.';
    }
}

// --- Navigation Handlers ---
document.getElementById('nav-home').addEventListener('click', (e) => {
    e.preventDefault();
    updateUI(); // Show default view based on login status
});

document.getElementById('nav-login').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('login-form-container').style.display = 'block';
    document.getElementById('register-form-container').style.display = 'none';
    // Hide all other sections
    document.getElementById('complaint-submission-section').style.display = 'none';
    document.getElementById('pdf-upload-section').style.display = 'none';
    document.getElementById('document-generation-section').style.display = 'none';
    document.getElementById('status-tracking-section').style.display = 'none';
});

document.getElementById('nav-register').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('login-form-container').style.display = 'none';
    document.getElementById('register-form-container').style.display = 'block';
    // Hide all other sections
    document.getElementById('complaint-submission-section').style.display = 'none';
    document.getElementById('pdf-upload-section').style.display = 'none';
    document.getElementById('document-generation-section').style.display = 'none';
    document.getElementById('status-tracking-section').style.display = 'none';
});

document.getElementById('nav-logout').addEventListener('click', (e) => {
    e.preventDefault();
    localStorage.removeItem('accessToken');
    updateUI();
    alert('Logged out successfully!');
});

// Add new nav link handler for circulars (assuming a nav item exists or will be added)
document.getElementById('nav-circulars').addEventListener('click', (e) => {
    e.preventDefault();
    // Hide other sections and show circulars section
    document.getElementById('auth-section').style.display = 'none';
    document.getElementById('complaint-submission-section').style.display = 'none';
    document.getElementById('pdf-upload-section').style.display = 'none';
    document.getElementById('document-generation-section').style.display = 'none';
    document.getElementById('status-tracking-section').style.display = 'none';
    document.getElementById('circulars-display-section').style.display = 'block';
    loadCirculars(); // Load circulars when navigating to this section
});

// --- Authentication Forms ---
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login_email').value;
    const password = document.getElementById('login_password').value;

    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch('/api/auth/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData.toString(),
    });
    const data = await response.json();

    if (response.ok) {
        localStorage.setItem('accessToken', data.access_token);
        alert('Login successful!');
        updateUI();
    } else {
        alert(`Login failed: ${data.detail || 'Unknown error'}`);
        displayResponse('loginResponse', data); // Display error details
    }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('register_email').value;
    const password = document.getElementById('register_password').value;
    const role = document.getElementById('register_role').value;

    const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password, role }),
    });
    const data = await response.json();

    if (response.ok) {
        alert('Registration successful! Please log in.');
        document.getElementById('login-form-container').style.display = 'block';
        document.getElementById('register-form-container').style.display = 'none';
        document.getElementById('login_email').value = email; // Pre-fill login email
        document.getElementById('login_password').value = '';
        displayResponse('registerResponse', { message: 'Registration successful! Please log in.' });
    } else {
        alert(`Registration failed: ${data.detail || 'Unknown error'}`);
        displayResponse('registerResponse', data); // Display error details
    }
});


// --- Initial UI setup on page load ---
document.addEventListener('DOMContentLoaded', updateUI);

// Complaint Submission
document.getElementById('complaintForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const citizen_id = document.getElementById('citizen_id').value;
    const description = document.getElementById('description').value;
    const language = document.getElementById('language').value;

    try {
        const response = await authenticatedFetch('/api/complaints', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ citizen_id, description, language }),
        });
        const data = await response.json();
        displayResponse('complaintResponse', data);
    } catch (error) {
        console.error('Error submitting complaint:', error);
    }
});

// PDF Upload
document.getElementById('pdfUploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    const pdfFile = document.getElementById('pdfFile').files[0];
    formData.append('file', pdfFile);

    try {
        const response = await authenticatedFetch('/api/upload-circular/', {
            method: 'POST',
            // No headers needed for FormData, browser sets multipart/form-data automatically
            body: formData,
        });
        const data = await response.json();
        displayResponse('pdfResponse', data);
    } catch (error) {
        console.error('Error uploading PDF:', error);
    }
});

// Document Generation - RTI
document.getElementById('rtiForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const applicant_name = document.getElementById('rti_applicant_name').value;
    const address = document.getElementById('rti_address').value;
    const information_sought = document.getElementById('rti_info_sought').value;
    const circular_id = document.getElementById('rti_circular_id').value;
    const complaint_id = document.getElementById('rti_complaint_id').value; // Get new complaint_id

    const payload = { applicant_name, address, information_sought };
    if (circular_id) payload.circular_id = circular_id; // Reverted to string
    if (complaint_id) payload.complaint_id = complaint_id; // Reverted to string

    try {
        const response = await authenticatedFetch('/api/generate-rti', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        const data = await response.text(); // Expecting HTML response now

        const rtiOutputContainer = document.getElementById('rtiOutputContainer');
        rtiOutputContainer.innerHTML = data; // Display HTML directly

    } catch (error) {
        console.error('Error generating RTI:', error);
        // Optional: display a user-friendly error message if generation fails
        document.getElementById('rtiOutputContainer').innerHTML = '<p style="color: red;">Failed to generate RTI document.</p>';
    }
});

// Document Generation - Scheme Application
document.getElementById('schemeAppForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const applicant_name = document.getElementById('scheme_applicant_name').value;
    const address = document.getElementById('scheme_address').value;
    const scheme_name = document.getElementById('scheme_name').value;
    const required_documents = document.getElementById('scheme_docs').value.split(',').map(doc => doc.trim()).filter(doc => doc);
    const circular_id = document.getElementById('scheme_circular_id').value;

    const payload = { applicant_name, address, scheme_name, required_documents };
    if (circular_id) payload.circular_id = circular_id;

    try {
        const response = await authenticatedFetch('/api/generate-scheme-application', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        const data = await response.text();
        document.getElementById('schemeAppResponse').innerHTML = data;
    } catch (error) {
        console.error('Error generating Scheme Application:', error);
    }
});

// Document Generation - Official Notice
document.getElementById('noticeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const recipient = document.getElementById('notice_recipient').value;
    const sender = document.getElementById('notice_sender').value;
    const subject = document.getElementById('notice_subject').value;
    const body = document.getElementById('notice_body').value;
    const complaint_id = document.getElementById('notice_complaint_id').value;
    const circular_id = document.getElementById('notice_circular_id').value;

    const payload = { recipient, sender, subject };
    if (body) payload.body = body;
    if (complaint_id) payload.complaint_id = complaint_id;
    if (circular_id) payload.circular_id = circular_id;

    try {
        const response = await authenticatedFetch('/api/generate-official-notice', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        const data = await response.text();
        document.getElementById('noticeResponse').innerHTML = data;
    } catch (error) {
        console.error('Error generating Official Notice:', error);
    }
});

// Document Generation - Work Order
document.getElementById('workOrderForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const complaint_id = document.getElementById('work_order_issue_id').value; // Now this is complaint_id
    const assigned_department = document.getElementById('work_order_dept').value;
    const task_description = document.getElementById('work_order_desc').value;
    const estimated_cost = parseFloat(document.getElementById('work_order_cost').value);
    const suggested_actions = document.getElementById('work_order_actions').value.split(',').map(action => action.trim()).filter(action => action);

    // New fields for WorkOrder
    const caller_name = document.getElementById('work_order_caller_name') ? document.getElementById('work_order_caller_name').value : null;
    const caller_contact = document.getElementById('work_order_caller_contact') ? document.getElementById('work_order_caller_contact').value : null;

    const payload = {};
    if (complaint_id) payload.complaint_id = complaint_id; // Send complaint_id
    if (assigned_department) payload.assigned_department = assigned_department;
    if (task_description) payload.task_description = task_description;
    if (!isNaN(estimated_cost)) payload.estimated_cost = estimated_cost;
    if (suggested_actions.length > 0) payload.suggested_actions = suggested_actions;
    if (caller_name) payload.caller_name = caller_name;
    if (caller_contact) payload.caller_contact = caller_contact;

    try {
        const response = await authenticatedFetch('/api/generate-work-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload),
        });
        const data = await response.json(); // Expecting JSON response

        document.getElementById('workOrderResponse').innerHTML = data.generated_html; // Display generated HTML

        // Populate form fields with data returned from backend (including pre-filled complaint data)
        if (data.complaint_id) document.getElementById('work_order_issue_id').value = data.complaint_id;
        if (data.assigned_department) document.getElementById('work_order_dept').value = data.assigned_department;
        if (data.task_description) document.getElementById('work_order_desc').value = data.task_description;
        if (data.estimated_cost !== undefined) document.getElementById('work_order_cost').value = data.estimated_cost;
        if (data.suggested_actions) document.getElementById('work_order_actions').value = data.suggested_actions.join(', ');
        if (data.caller_name) {
            // Ensure caller_name input exists before trying to set its value
            const callerNameInput = document.getElementById('work_order_caller_name');
            if (callerNameInput) callerNameInput.value = data.caller_name;
        }
        if (data.caller_contact) {
            // Ensure caller_contact input exists before trying to set its value
            const callerContactInput = document.getElementById('work_order_caller_contact');
            if (callerContactInput) callerContactInput.value = data.caller_contact;
        }

    } catch (error) {
        console.error('Error generating Work Order:', error);
        document.getElementById('workOrderResponse').innerHTML = '<p style="color: red;">Failed to generate Work Order.</p>';
    }
});

// Status Tracking
document.getElementById('statusTrackForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const complaint_id = document.getElementById('track_complaint_id').value;

    try {
        const response = await authenticatedFetch(`/api/complaints/${complaint_id}`);
        const data = await response.json();
        displayResponse('statusResponse', data);
    } catch (error) {
        console.error('Error tracking status:', error);
    }
});
