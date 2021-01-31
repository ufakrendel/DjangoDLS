let id_val = ''

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

$(document).ready(async function(){
    const element = $( "#file_id" );
    if (element) {
        id_val = element[0].value
    };

    if (!id_val) {
        console.log("Error in receive file Id!");
        return;
    }

    let isError = false

    await chekData();

  });

let timeleft = 0;
chekData = async function (){
    let result = await getData()
    console.log("We get result: " + result)

    if (result === false){
        console.log('Error')
        return
    }

    if (result.includes('ENDED')){
        console.log("result ENDED!!!")
        let url = 'get_by_id/' + id_val;
        window.location.replace(url);
    }
    timeleft = timeleft + 1;
    document.getElementById("timeleft").textContent= timeleft.toString() + ' c.';
    setTimeout(chekData, 1000)
}

getData = async function (){
    let result = ''
    await $.get(("result_by_id/" + id_val) , {"file_id": id_val})
            .done(function(request) {
                    result = request
                })
            .fail(function() {
                alert( "Ошибка в обработке! Попробуйте еще раз." );
                result = false;
            });
    return result
}
