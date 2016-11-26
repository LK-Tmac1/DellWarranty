## Dell Warranty Search Web App

####Use case

Search warranty of dell devices from Dell Warranty API by using service tags (svctag).

Service tag is a 7 digits of characters and/or numbers used to identify an dell device. Say DG5QYW1 is Latitude E6430.

1. Input: part of a service tag, say the first 4 are fixed as DG5Q while the last three are unknown. 
2. Output: based on part of a service tag, reterive all dell warranty info of those valid service tags.

####Challenge: design the workflow

1. How to get all valid service tags?

  Use itertools.product method to generate Cartesian product by using the part svctag. Then use an URL from Dell to check one by one if a svctag is valid or not based on the response from the request with the svctag as parameter.
  
2. ssss

####Reference

More about the searching: http://www.dell.com/support/home/en/cndhs1/Products/?app=warranty

More about the API: http://en.community.dell.com/dell-groups/supportapisgroup/

Python lib used in this project:

1. flask
2. requests
3. xlsxwriter
4. re
5. itertools
6. yaml
