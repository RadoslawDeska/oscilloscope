illuminated_button_style = """
                            QPushButton {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #FFFFFF, stop:1 #a4a8a8);
                                border: 2px solid #666666;
                                border-radius: 5px;
                                padding: 5px;
                            }

                            QPushButton:pressed {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #F8FFEF, stop:1 #b9ff67);
                                border: 2px solid #333333;
                                border-radius: 5px;
                                padding-top: 7px;
                                padding-left: 7px;
                            }

                            QPushButton:checked {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #F8FFEF, stop:1 #b9ff67);
                                border: 2px solid #666666;
                                border-radius: 5px;
                                padding: 5px;
                            }

                            QPushButton:checked:pressed {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #F8FFEF, stop:1 #b9ff67);
                                border: 2px solid #333333;
                                border-radius: 5px;
                                padding-top: 7px;
                                padding-left: 7px;
                            }
                            
                            #runStop_button:!checked {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #F8FFEF, stop:1 #ff0000); /* red */
                            }
                            
                            #runStop_button:pressed {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #F8FFEF, stop:1 #b9ff67); /* green */
                                padding-top: 7px;
                                padding-left: 7px;
                            }
                            
                            #runStop_button:checked {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #F8FFEF, stop:1 #b9ff67); /* green */
                                padding: 5px;
                            }
                            
                            #runStop_button:disabled {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #FFFFFF, stop:1 #a4a8a8);
                                border: 2px solid #666666;
                                border-radius: 5px;
                                padding: 5px;
                            }
                                                        
                            #onOff_button:!checked {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                                        stop:0 #FFFFFF, stop:1 #fffce0);
                                border-radius: 15px;
                                padding: 5px;
                            }
                            
                            #onOff_button:pressed {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #F8FFEF, stop:1 #b9ff67); /* green */
                                border-radius: 15px;
                                padding-top: 7px;
                                padding-left: 7px;
                            }
                            
                            #onOff_button:checked {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #F8FFEF, stop:1 #b9ff67); /* green */
                                border-radius: 15px;
                                padding: 5px;
                            }
                            
                            #onOff_button:disabled {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, 
                                                        stop:0 #FFFFFF, stop:1 #fffce0);
                                border-radius: 15px;
                                padding: 5px;
                            }
                            
                            #onOff_button:checked:pressed {
                                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                                                        stop:0 #F8FFEF, stop:1 #b9ff67);
                                border-radius: 15px;
                                padding-top: 7px;
                                padding-left: 7px;
                            }
                            
                            """
