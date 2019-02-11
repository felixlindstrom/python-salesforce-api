<env:Envelope xmlns:xsd='http://www.w3.org/2001/XMLSchema'
xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance'
xmlns:env='http://schemas.xmlsoap.org/soap/envelope/'>
    <env:Body>
        <sf:login xmlns:sf='urn:enterprise.soap.sforce.com'>
            <sf:username>{username}</sf:username>
            <sf:password>{password}</sf:password>
        </sf:login>
    </env:Body>
</env:Envelope>