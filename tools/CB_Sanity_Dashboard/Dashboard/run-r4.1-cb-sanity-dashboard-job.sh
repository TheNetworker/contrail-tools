echo "Creating the final.json"
execfolder="/tmp/r4.1-cb-sanity"
mkdir -p ${execfolder}
cp /root/sanity-dashboard/sanity_summary_tool.py ${execfolder}
cp /root/sanity-dashboard/displaytemplate.py ${execfolder}
cp /root/sanity-dashboard/merge_jsons_dashboard.py ${execfolder}
cd ${execfolder}
python sanity_summary_tool.py --mode r4.1-cb-sanity --outfile_cb r4.1-cb-sanity-result.json --outfile_fb r4.1-fb-sanity-result.json
python merge_jsons_dashboard.py --cb_json r4.1-cb-sanity-result.json --fb_json r4.1-fb-sanity-result.json --outfile r4.1-cb-sanity-final-result.json
echo "now lets transfer the file to the jenkins slave"
sshpass -p c0ntrail123 scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${execfolder}/r4.1-cb-sanity-final-result.json root@10.84.24.64:/cs-shared/sanity-db/r4.1-cb-sanity-final-result.json
rm -f *ini
#rm -f *py
#rm -f *json
echo "Done"

