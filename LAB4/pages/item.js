let url = window.location.href;
let num = parseInt(url.substring(url.lastIndexOf("/")+1));

fetch('../products.json', {method:"GET"})
    .then((response) => {return response.json()})
    .then((data) => {
        let products = data;
        if(data.length < num){
            window.location.href = 'not_found'
        }else{
            products.map(function(products){
                document.getElementById('item_name').innerHTML = `${products.name}`
                document.getElementById('author').innerHTML = `${products.author}`
                document.getElementById('price').innerHTML = `${products.price}`
                document.getElementById('desc').innerHTML = `${products.description}`
        })
        }
    });
