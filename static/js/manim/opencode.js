function opencode(codeId) {
    //Get code_text and pass it to the editor
    if (codeId) {
        fetch(`get_code_text/${codeId}/`)
            .then(response => {
                if (!response.ok) { //to get readeable error from ajax fetch request 
                    return response.text().then(text => { throw new Error(text); });
                }
                return response.json();
            })
            .then(data => {
                console.log('Received code text:', data.code_text);
                // document.getElementById("code").value = data.code_text;
                editor.setValue(data.code_text);

                // set current code name so that it enables updating/saving the code 
                console.log(`code_name: ${data.code_name}`)
                setCodeName(data.code_name);

                // update current code UI text
                document.getElementById(
                    "current-project-name"
                ).textContent = data.code_name;

                // Send updated code to server
                // This is to ensure that even if the site is refreshed, the selected code remains.
                return fetch('update-code/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{{ csrf_token }}'  // Ensure CSRF token is included
                    },
                    body: JSON.stringify({ code_text: data.code_text })
                });
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(text => { throw new Error(text); });
                }
                return response.json();
            })
            .then(result => {
                console.log('Update status:', result.status);
                if (result.status === 'success') {
                    console.log('Django variable updated:', result.code_text);
                } else {
                    console.log('Failed to update Django variable');
                }
            })
            .catch(error => console.error('Error:', error));
    } else {
        // document.getElementById("code").value = '';
    }
}


function setCodeName(codeName) {
    fetch('set_code_name/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value, // Ensure CSRF token is included
        },
        body: JSON.stringify({ code_name: codeName }) // Pass the data
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log(data.message);
            } else {
                console.error(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });

    const inputCode = document.getElementById('code').value;
    console.log('inputCode:', inputCode)
}