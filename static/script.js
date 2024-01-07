document.getElementById('generateButton').addEventListener('click', function() {
    fetch('http://localhost:8000/generate_embeddings')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // Change the button text after the embeddings are generated
            document.getElementById('generateButton').textContent = 'Change Embeddings';
        }).catch(error => {
            console.log('There was a problem with the fetch operation: ' + error.message);
        });
});


document.getElementById('retrieveButton').addEventListener('click', function() {
    var query = document.getElementById('queryInput').value;
    fetch('http://localhost:8000/retrieve_embeddings/' + query)
        .then(response => response.json())
        .then(data => {
            let responseText = data.results;
            

            // responseText = responseText.replace(/\\n/g, '<br>');
            // responseText = responseText.replace(/\\"/g, '"');
            // console.log({"responseText":responseText})
            document.getElementById('results').innerHTML = responseText;

        });
});

document.getElementById('uploadButton').addEventListener('click', function() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];
    var formData = new FormData();
    formData.append("file", file);
    fetch('http://localhost:8000/uploadfile/', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    }).catch(error => {
        console.log('There was a problem with the fetch operation: ' + error.message);
    });
});

