let ul = document.getElementById('product_list');

fetch('products.json', {method:"GET"})
    .then((response) => {return response.json()})
    .then((data) => {
        let products = data;
        let i=1;
        products.map(function(products){
            let li = document.createElement('li');
            let name = document.createElement('h4');
            let link = document.createElement('a');

            name.innerHTML = `${products.name}`;
            link.innerHTML = `See Product`;
            link.href = `/products/`+i;
            i++;

            li.appendChild(name);
            li.appendChild(link);
            ul.appendChild(li);
        })
    });
