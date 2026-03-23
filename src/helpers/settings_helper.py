import yaml
import streamlit as st
import time

class SettingsConfiguration:
    def __init__(self, path):
        self.path = path
        with open(path, 'r') as file:
            self.settings_data = yaml.safe_load(file)

    def get_settings(self):
        return self.settings_data

    def update_settings(self, key, value, rerun=True):
        self.settings_data[key] = value
        with open(self.path, 'w') as file:
            yaml.dump(self.settings_data, file)
        if rerun:
            time.sleep(0.5)
            st.rerun()
