# Credentials: admin:password -> Authorization: Basic YWRtaW46cGFzc3dvcmQ=
# Wrong Credentials: admin:admin -> Authorization: Basic YWRtaW46YWRtaW4=

curl --location --request PATCH '127.0.0.1:8080/UE/patch' \
--header 'Content-Type: application/json' \
--header 'Authorization: Basic YWRtaW46YWRtaW4=' \
--data '{
    "IMSI": 1, 
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