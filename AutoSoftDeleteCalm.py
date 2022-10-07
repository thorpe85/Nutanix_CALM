import datetime

#Prism Central variables settings
pc_api_user = '@@{cscalm.username}@@'
pc_api_password = '@@{cscalm.secret}@@'

pc_api_fqdn = '10.0.0.11'
pc_headers = {'Content-Type': 'application/json'}


pc_payload = {'kind':'app', 'length': 250}
pc_api_url = 'https://'+pc_api_fqdn+':9440/api/nutanix/v3/'

teams_webhook_url = 'https://nutafr.webhook.office.com/webhookb2/efe548158885515154ce034d3cd@1c5e18ad-c339-465657dd8f333-976ebd5/IncomingWebhook/60aeeeeee47208bcab512588-5151144-83'


start_payload = '{"type":"MessageCard","themeColor":"0072C6", "title":"Calm SoftDelete Apps Summary","summary":"summary","text": "Calm SoftDelete Apps Summary", "sections": [{ "facts" : ['      
end_payload = ']}]}'

rows  = ''

retentionDays = 3

# Get List of Apps from Prism Central limit 250

nutanix_response = urlreq(pc_api_url+'apps/list', verb='POST', auth='BASIC', user=pc_api_user, passwd=pc_api_password, params=json.dumps(pc_payload), headers=pc_headers)

if nutanix_response.ok: 
     entities_nutanix =  json.loads(nutanix_response.content)
     print(entities_nutanix)
     # iterate on each apps and get name and uuid
     for i in entities_nutanix['entities']:

         app_name = i['status']['name']       
         app_uuid = i['status']['uuid']
         app_creation_time = i['status']['creation_time']
         app_creation_time = datetime.datetime.fromtimestamp(app_creation_time/1000000)
         today_time = datetime.datetime.now()
              
         time_difference = today_time - app_creation_time
         print(time_difference.days)
         # if apps is older than 3 days, app will be soft delete
         if time_difference.days >= retentionDays:
             print(app_name+' is older than '+str(time_difference.days)+' days')
             
             app_delete_response = urlreq(pc_api_url+'apps/'+app_uuid+'?type=soft', verb='DELETE', auth='BASIC', user=pc_api_user, passwd=pc_api_password, headers=pc_headers)
             if app_delete_response.ok:
                 row = '{ "name": "'+app_name+'" , "value" : "'+app_name+' is older than '+str(time_difference.days)+' days'+' and soft delete has been initiated" }'
                 rows = rows+row+','
         else:
             print(app_name+' is younger than '+str(time_difference.days)+' days')
     # All soft delete apps trace are sent to a Teams Webhook
     payload_teams =  start_payload+rows+end_payload
     print(payload_teams)
     teams_reponse = urlreq(teams_webhook_url, verb='POST', params=payload_teams, headers=pc_headers)
     if teams_reponse.ok:
         print('webhook call', teams_reponse.content)
     else:
         print('request failed', teams_reponse.content)
         exit(1)
         

else: 
    print('request failed', nutanix_response.content)
    exit(1)