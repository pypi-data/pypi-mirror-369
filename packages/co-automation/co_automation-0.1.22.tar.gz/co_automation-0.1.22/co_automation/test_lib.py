from co_automation import create_change_order
co = create_change_order.create_change_order(
"adp-test", #Service Now Instance
"test_token", #Token
"Salesforce Service_IAT", #CO Item
"11-11-2024", #start date
"11-12-2024", #end date
"10", #year week
"sudip.nath@adp.com", #requested by
"DC1", #data center
"IAT", #env
(f"Salesforce Service IAT: Scheduled Deployment of CAET Salesforce Release"), #short description
(f"Salesforce Service:  \n"
                           f"Scheduled Development work for Salesforce IAT, the code is tested in the QA environment and signed off by QA \n"
                           "Code deployment- \n"
                           "Packages to be deployed (as per deployment instructions for specific Build/ builds): https://confluence.es.ad.adp.com/display/CAETSF/Salesforce"
),#long description
"urgent", #business case
"test_plan", #communication plan
"critical", #impact analysis
"no_rollback", #backout plan
"test_plan", #test plan
True #is test mode
)
print(co)