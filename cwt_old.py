# @app.route('/cwt', methods=['GET', 'POST'])
# def get_cwt_list():
#     """
#     Process ECG data uploaded as binary and return CWT-transformed segments.
#     """
#     try:
#         # parse json data
#         data = request.get_json()

#         # Validate User ID
#         userid = request.headers.get('userid')
#         if not userid or not User.query.get(userid):
#             return jsonify({"error": "invalid or missing userid"}), 400
        
#         userid = data['userid']
        
#         # Read binary data from the request
#         raw_data = request.data  # Flask stores raw binary data in request.data
#         dtype = np.dtype(np.float32).newbyteorder('>')
#         data = np.frombuffer(raw_data, dtype=dtype)

#         # Log the received data for debugging
#         print("Raw data received:", data)
#         print("Length of raw data:", len(data))

#         if len(data) < 18:
#             return jsonify({"error": "input data length must be greater than 18"}), 400
        
        
#         # Process ECG data
#         data = nk.ecg_clean(data, sampling_rate=sample_rate)
#         processed_data, _ = nk.ecg_process(data, sampling_rate=sample_rate)
#         rpeaks = np.nonzero(np.array(processed_data['ECG_R_Peaks']))[0]
#         n_rpeaks = len(rpeaks)

#         # Initialize results
#         item_list = []

#         # Extract segments and compute CWT
#         for i in range(min(n_rpeaks - 2, n_choices)):
#             segment = data[
#                 rpeaks[i + rpeak_offset] - before_rpeak:rpeaks[i + rpeak_offset] + after_rpeak + 1
#             ]
#             segment, _ = pywt.cwt(segment, scales, waveletname)
#             segment = Image.fromarray(segment.astype(np.float32))
#             resized_segment = segment.resize(output_size)
#             item_list.append({"values": list(resized_segment.getdata())})

#         # Store raw ecg data
#         ecg_scan_key = f"scan_{datetime.timezone.utc().strftime('%Y%m%d%H%M%S')}"
#         new_ecg = ECG(userid=userid, ecg_scan_key=ecg_scan_key, raw_ecg_data=data.tobytes)
#         db.session.add(new_ecg)
#         db.session.commit()

#         # Return the results as JSON
#         # Retrieve the ecg result in json format by performing GET request on "raw_data" 
#         return jsonify({
#             "user_id": userid,
#             "ecg_scan_key": ecg_scan_key,
#             "raw_data": data.tolist(),  # Convert NumPy array to list for JSON serialization
#             "items": item_list
#         }), 200

#     except Exception as e:
#         print("Error during processing:", str(e))
#         return jsonify({"error": str(e)}), 500
    