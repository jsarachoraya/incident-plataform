console.log("Aplicacion iniciada correctamente.");

function confirmarEliminacion(){
    return confirm("¿Seguro que querés eliminar esta incidencia?");
}

function actualizarCamposOrigen() {
    const origen = document.getElementById("origen");
    const campoCliente = document.getElementById("campo_cliente");
    const campo_Legajo = document.getElementById("campo_legajo");

    if (!origen || !campoCliente || !campo_legajo) {
        return;
    }

    if (origen.value === "cliente") {
        campoCliente.style.display = "block";
        campo_Legajo.style.display = "none";
    } else {
        campoCliente.style.display = "none";
        campo_Legajo.style.display = "block";
    }
}

document.addEventListener("DOMContentLoaded", function() {
    actualizarCamposOrigen();

    const origen = document.getElementById("origen");

    if (origen) {
        origen.addEventListener("change", actualizarCamposOrigen);
    }
});
