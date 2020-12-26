// delete  action for the fyyur app 


const deleteButton = document.querySelector("#delete_button")

deleteButton.addEventListener('click' , (event) => {
    event.preventDefault()
    const venue_id = event.target.dataset.id
    console.log(venue_id)

    fetch(`/venues/${venue_id}` , {
        method:"DELETE"
    }).then(res => window.location = res.url)
})