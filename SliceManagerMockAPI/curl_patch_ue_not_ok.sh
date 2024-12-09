# Credentials: admin:password
curl --location --request PATCH '127.0.0.1:8080/UE/patch' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic YWRtaW46cGFzc3dvcmQ=' \
--data '{
    "IMSI": -1, 
    "numIMSIs":2, 
    "slice": "second_slice", 
    "IPV4": "", 
    "IPV6": "", 
    "AMDATA": true, 
                    
    "DEFAULT": "TRUE",  
                        
    "UEcanSendSNSSAI": "TRUE",   
                                
    "AMBRUP": 2000000,  
    "AMBRDW": 2000000   
}'