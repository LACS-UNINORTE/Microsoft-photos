const btnDelete = document.querySelectorAll('.btn-delete');
if (btnDelete) {
  const btnArray = Array.from(btnDelete);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if (!confirm('¿Estás seguro de realizar esta acción?')) {
        e.preventDefault();
      }
    });
  });
}

const btnValidar = document.querySelectorAll('.btn-validar');
if (btnValidar) {
  const btnArray2 = Array.from(btnValidar);
  btnArray2.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if (!confirm('¿Estás seguro de realizar esta acción?')) {
        e.preventDefault();
      }
    });
  });
}
