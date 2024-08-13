 while self.connected:
            dataRO = self.getRO(3) # robot output #3 => KissValve Opens
            print(dataRO)
            while dataRO != 0:
                # dataRO = self.getRO(3) 
                data = self.getReg(37) # register #37 => Loadcell
                # print(data)
                # Append the data to the variable for writing to CSV
                self.data_to_write.append(data)
                if dataRO == 0:
                    # ANALYZING LOGIC COULD BE HERE OR MAYBE WAIT UNTIL YOU HIT ANALYZE BUTTON GETS CLICKED
                    # AND THEN DO THE ANALYSIS, ANYWAYS IN ORDER TO SAVE THE BATCH YOU MUST FIRST HAVE ALL FIELDS.4
                    # ADD CHECK FOR ENSURING AL FILEDS ARE PRESENT BEFORE SAVING DATA. 
                    ##########################################################################################################
                    ##########################################################################################################
                    ########################################## WORKING STARTS HERE ##################################################
                    ##########################################################################################################
                    ##########################################################################################################
                    self.cap_successful = True
                    target_length = 100
                    normalized_index, normalized_data = self.interpolate_and_normalize(
                        data, target_length
                    )

                    # Calculate differences between consecutive points
                    differences = np.diff(normalized_data) * 100

                    # Check if any value in the last 20 elements of the differences list is over 5
                    if any(abs(diff) > 5 for diff in differences[-20:]):
                        print(
                            f"At least one value in the last 20 elements differences is over 5."
                        )
                        self.cap_successful = False
                        # result_label = customtkinter.CTkLabel(
                        #     self.scrollable_frame, text="Failed", text_color="red"
                        # )
                        # # toggle_var.set("0")
                    else:
                        print(
                            f"No value in the last 20 elements differences is over 5."
                        )
                        self.cap_successful = True
                        # result_label = customtkinter.CTkLabel(
                        #     self.scrollable_frame, text="Passed", text_color="green"
                        # )
                        # # toggle_var.set("1")
                    ##########################################################################################################
                    ##########################################################################################################
                    ########################################## WORKING ENDS HERE ##################################################
                    ##########################################################################################################
                    ##########################################################################################################
                    
                    self.current_batch.append(
                            {
                            "cap_id": capNo,
                            "cap_successful": self.cap_successful,
                            "cap_load_cell_data": self.data_to_write,
                            }
                        )
                    capNo += 1
                    print()
                    self.data_to_write = []
                    break
