document.getElementById("surveyForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Evita la recarga de la página

    const json = {};

    // Añadir interacción: Cambia el color del cuadro al seleccionar un checkbox
    document.querySelectorAll(".option input[type='radio']").forEach(input => {
        input.addEventListener("change", () => {
            if (input.checked) {
                input.closest(".option").classList.add("selected");
            } else {
                input.closest(".option").classList.remove("selected");
            }
        });
    });



    const formElements = this.elements;
    console.log(formElements)

    // Recorremos los elementos del formulario
    for (let element of formElements) {
        if (element.type === "radio" || element.type === "checkbox") {
            // Si es un radio o checkbox, sólo agregamos el valor si está seleccionado
            if (element.checked) {
                if (json[element.name]) {
                    // Si ya existe la clave, agregamos el valor (en caso de varios checkboxes)
                    if (Array.isArray(json[element.name])) {
                        json[element.name].push(element.value);
                    } else {
                        json[element.name] = [json[element.name], element.value];
                    }
                } else {
                    json[element.name] = element.value;
                }
            }
        } else if (element.name) {
            // Para otros elementos, simplemente agregamos el valor
            json[element.name] = element.value;
        }
    }

    try {
        const response = await fetch("http://127.0.0.1:8000/recibir-datos", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",  // Asegúrate de que se envíe como JSON
            },
            body: JSON.stringify(json),  // Los datos se envían como JSON
        });

        if (response.redirected) {
            window.location.href = response.url;  // Redirige automáticamente a `/resultados`
        } else {
            const respuesta = await response.text()
            console.log("Respuesta recibida:", respuesta);
            document.body.innerHTML = respuesta;
        }
    } catch (error) {
        console.error("Error al enviar los datos:", error);
        alert(`Hubo un error al enviar los datos. Detalles: ${error.message}`);
    }
});

// Función para recolectar los datos del formulario y enviarlos a la API en formato JSON
function submitForm(event) {
  event.preventDefault(); // Prevenir que el formulario se envíe de forma tradicional

console.log("hola")
jkewldjck

  const formData = {};
  const formElements = document.getElementById("surveyForm").elements;

  // Recorremos los elementos del formulario
  for (let element of formElements) {
    if (element.type === "radio" || element.type === "checkbox") {
      // Si es un radio o checkbox, sólo agregamos el valor si está seleccionado
      if (element.checked) {
        if (formData[element.name]) {
          if (Array.isArray(formData[element.name])) {
            formData[element.name].push(element.value);
          } else {
            formData[element.name] = [formData[element.name], element.value];
          }
        } else {
          formData[element.name] = element.value;
        }
      }
    } else if (element.name) {
      formData[element.name] = element.value;
    }
  }

  // Enviar los datos como JSON a la API
  fetch("/recibir-datos", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.json())
    .then((data) => {
      // Redirigir o mostrar un mensaje al usuario después de enviar los datos
      window.location.href = "/resultados";
    })
    .catch((error) => {
      console.error("Error al enviar los datos:", error);
      alert(`Hubo un error al enviar los datos. Detalles: ${error.message}`);
    });
}

// Función para mantener seleccionadas las opciones cuando la página se recarga
function keepSelections() {
  const formElements = document.getElementById("surveyForm").elements;

  for (let element of formElements) {
    if ((element.type === "radio" || element.type === "checkbox") && localStorage.getItem(element.name)) {
      const storedValue = localStorage.getItem(element.name);
      if (element.type === "radio") {
        if (element.value === storedValue) {
          element.checked = true;
        }
      } else if (element.type === "checkbox") {
        if (storedValue.split(",").includes(element.value)) {
          element.checked = true;
        }
      }
    }
  }
}

// Al enviar el formulario, guardar los valores seleccionados en localStorage
window.addEventListener("load", function () {
  keepSelections();

  document.getElementById("surveyForm").addEventListener("submit", function () {
    const formElements = this.elements;
    for (let element of formElements) {
      if (element.checked) {
        if (element.type === "radio" || element.type === "checkbox") {
          localStorage.setItem(element.name, element.value);
        }
      }
    }
  });
});


