# 192.168.100.173


Invoke-WebRequest `
 -Uri http://192.168.100.173:8000/logs `
 -Method POST `
 -Headers @{ "Content-Type"="application/json" } `
 -Body '{ "source":"windows11","event":"failed_login","message":"test","timestamp":"2025-12-22" }'


Invoke-WebRequest `
 -Uri http://192.168.100.173:8000/logs `
 -Method POST `
 -Headers @{ "Content-Type"="application/json" } `
 -Body '{ "source":"windows11","event":"failed_login","message":"test","timestamp":"2025-12-22" }'
