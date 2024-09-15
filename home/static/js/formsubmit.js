let _url = window.location.toString().split(window.location.host.toString())[1];
let cargando = '<i class="fa fa-cog fa-spin" role="status" aria-hidden="true"></i>';
let error_btn2 = '<i class="fa fa-check-circle" role="status" aria-hidden="true"></i> Guardar';
let method_req = "POST";
let _enc = $('*[data-datoseguro=true]').toArray();
let headerId = '#header';
let __enc = [];
for (let i = 0; i < _enc.length; i++) {
    __enc.push($(_enc[i]).attr('name'));
}
let inputsEncrypted = __enc.join('|');

$(function () {
    $('form:not([method=GET], [method=get])').submit(function (e) {
        e.preventDefault();
        if (typeof funcionAntesDeGuardar === 'function') {
            funcionAntesDeGuardar();
        }
        const formulario = $(this);
        console.log(formulario);
        const btnSubmit = $('#submit,#submit2,#submit3');
        const error_btn = btnSubmit.html();
        $('input, textarea, select').removeClass('is-invalid');
        const pk = formulario.find('input[name=pk]').length ? parseInt(formulario.find('input[name=pk]').val()) : 0;
        const action = formulario.find('input[name=action]').length ? formulario.find('input[name=action]').val() : false;
        const _url = formulario.find('input[name=urlsubmit]').length ? formulario.find('input[name=urlsubmit]').val() : window.location.toString().split(window.location.host.toString())[1];
        var _form = new FormData(formulario[0]);
        console.log(new FormData(formulario[0]))
        if (pk !== 0) {
            if (_form.has('pk')) {
                _form.set('pk', pk.toString());
            } else {
                _form.append('pk', pk.toString());
            }

        }
        if (action !== false) {
            if (_form.has('action')) {
                _form.set('action', action);
            } else {
                _form.append('action', action);
            }
        }
        const listInputsEnc = inputsEncrypted.split('|');
        for (var i = 0; i < listInputsEnc.length; i++) {
            if (_form.has(listInputsEnc[i])) {
                _form.set(listInputsEnc[i], doRSA(_form.get(listInputsEnc[i])));
            }
        }
        try {
            _form.append("lista_items1", JSON.stringify(lista_items1));
        } catch (err) {
            console.log(err.message);
        }
        console.log({
            type: method_req,
            url: _url,
            data: _form,
        })
        $.ajax({
            type: method_req,
            url: _url,
            data: _form,
            dataType: "json",
            enctype: formulario.attr('enctype'),
            cache: false,
            contentType: false,
            processData: false,
            beforeSend: function () {
                btnSubmit.html(cargando);
                btnSubmit.attr("disabled", true);
                bloqueointerface();
            }
        }).done(function (data) {
            console.log(data)
            if (!data.result) {
                // Hide modal if it exists
                if (data.modalname) {
                    $('#' + data.modalname).modal('hide');
                } else {
                    $(".modal").modal('hide');
                }

                // Redirect if specified
                if (data.to) {
                    window.location.href = data.to;
                }

                // Optionally handle error messages
                if (data.error) {
                    // Display error message to the user
                    dangerNotify(data.error);
                }
            } else {
                // Handle successful login or other actions
                if (data.to) {
                    window.location.href = data.to;
                }
            }

            // if (!data.result) {
            //     if (data.modalname) {
            //         $('#' + data.modalname).modal('hide');
            //     } else {
            //         $(".modal").modal('hide');
            //     }
            //     if (data.to) {
            //         if (data.modalsuccess) {
            //             $.unblockUI();
            //             $('#textpanelmensaje').html(data.mensaje);
            //             $('#returnpanelmensaje').attr("href", data.to);
            //             $('#waitpanelmensaje').modal({backdrop: 'static'}).modal('show');
            //         } else {
            //             location = data.to;
            //         }
            //     } else if (data.cerrar) {
            //         $.unblockUI();
            //         Swal.fire(data.mensaje, '', 'success')
            //     } else if (data.funcion) {
            //         $.unblockUI();
            //         ajaxResponse(data)
            //     } else {
            //         if (data.modalsuccess) {
            //             $.unblockUI();
            //             $('#textpanelmensaje').html(data.mensaje);
            //             $('#returnpanelmensaje').attr('onClick', 'location.reload()');
            //             $('#waitpanelmensaje').modal({backdrop: 'static'}).modal('show');
            //         } else {
            //             location.reload();
            //         }
            //
            //     }
            // } else if (data.data_return) {
            //     $.unblockUI();
            //     successNotify(data.mensaje)
            //     btnSubmit.html(error_btn2);
            //     btnSubmit.attr("disabled", false);
            //     ActualizarTabla(data.data)
            // } else {
            //     if (data.form) {
            //         $(".mensaje_error").empty()
            //         data.form.forEach(function (val, indx) {
            //             var keys = Object.keys(val);
            //             keys.forEach(function (val1, indx1) {
            //                 $("#id_" + val1).addClass("is-invalid");
            //                 $("#errorMessage" + val1).html(val[val1]);
            //             });
            //         });
            //     }
            //     if (!data.typewarning)
            //         dangerNotify(data.mensaje);
            //     else
            //         warningNotify(data.mensaje);
            //     btnSubmit.html(error_btn2);
            //     btnSubmit.attr("disabled", false);
            //     $.unblockUI();
            // }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            dangerNotify("Error al enviar los datos");
            btnSubmit.html(error_btn2);
            btnSubmit.attr("disabled", false);
            $.unblockUI();
        }).always(function () {

        });
    });
});
