<html>
<head>
    <style type="text/css">
        ${css}
    </style>
</head>
<body>
    <h2>Corrispettivi</h2>
    <% setLang(objects[0].company_id.partner_id.lang or "en_US") %>
    <table style="width:100%;">
        <thead>
        <tr>
            <th style="text-align:left">Data registrazione</th>
            <th style="text-align:left">Descrizione</th>
            <th style="text-align:right">Importo totale</th>
            <th style="text-align:right">% IVA</th>
            <th style="text-align:right">Imponibile</th>
            <th style="text-align:right">Imposta</th>
            <th></th>
        </tr>
        </thead>
        <tbody>
        %for object in objects :
            %for line in tax_lines(object) :
                <tr><td>
                %if line['index']==0: 
                    ${ formatLang(object.date,date=True) or ''| entity}
                %endif
                </td><td>
                %if line['index']==0:
                    Corrispettivo
                %endif
                </td><td style="text-align:right">
                %if line['index']==0:
                    ${ formatLang(line['amount_total']) | entity}
                %endif
                </td>
                <td style="text-align:right">${ line['tax_percentage'] or ''| entity}</td>
                <td style="text-align:right">${ formatLang(line['base'])  or ''| entity}</td>
                <td style="text-align:right">${ formatLang(line['amount'])  or ''| entity}</td>
                <td></td>
                </tr>
            %endfor
        %endfor
        </tbody>
    </table>
    <div style="page-break-inside: avoid;">
        <br/>
        <table style="width:100%;  " border="1">
            <tr style="border-style:ridge;border-width:5px">
                <td colspan="3" style="padding:10; ">Periodo di stampa dal <strong>${formatLang(data['form']['date_from'],date=True)| entity}</strong> al <strong>${formatLang(data['form']['date_to'],date=True)| entity}</strong></td>
            </tr>
            <tr>
                <td rowspan="2" style="vertical-align:text-top;padding:10">
                    <table style="width:100%;">
                        <tr>
                            <th style="text-align:left">Descrizione</th>
                            <th style="text-align:right">Imponibile</th>
                            <th style="text-align:right">Imposta</th>
                        </tr>
                        %for tax_code in tax_codes :
                        <tr>
                            <td>${tax_code|entity}
                            </td><td style="text-align:right">${formatLang(tax_codes[tax_code]['base'])|entity}
                            </td><td style="text-align:right">${formatLang(tax_codes[tax_code]['amount']) or ''|entity}
                            </td>
                        </tr>
                        %endfor
                    </table>
                </td><td style="padding:10">Totale operazioni:<br/><p style="text-align:center"><strong>${formatLang(totali['totale_operazioni'])|entity}</strong></p><br/></td>
                <td style="padding:10">Totale imponibili:<br/><p style="text-align:center"><strong>${formatLang(totali['totale_imponibili'])|entity}</strong></p><br/></td>
            </tr>
            <tr>
                <td style="padding:10">Totale variazioni:<br/><p style="text-align:center"><strong>${formatLang(totali['totale_variazioni'])|entity}</strong></p><br/></td>
                <td style="padding:10">Totale IVA:<br/><p style="text-align:center"><strong>${formatLang(totali['totale_iva'])|entity}</strong></p><br/></td>
            </tr>
        </table>
    </div>
</body>
</html>
