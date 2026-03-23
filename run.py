import streamlit
  import streamlit.web.cli as stcli
  import os
  import sys
  import shutil


  def resolve_path(path):
      if getattr(sys, 'frozen', False):
          bundle_dir = sys._MEIPASS
      else:
          bundle_dir = os.getcwd()
      resolved_path = os.path.abspath(os.path.join(bundle_dir, path))
      return resolved_path


  if __name__ == "__main__":
      home_dir = os.path.expanduser('~')
      user_streamlit_dir = os.path.join(home_dir, '.streamlit')
      os.makedirs(user_streamlit_dir, exist_ok=True)

      bundled_config = resolve_path(os.path.join('.streamlit', 'config.toml'))
      user_config = os.path.join(user_streamlit_dir, 'config.toml')
      shutil.copy2(bundled_config, user_config)

      sys.argv = [
          "streamlit",
          "run",
          resolve_path(os.path.join("src", "app.py")),
          "--global.developmentMode=false",
      ]
      sys.exit(stcli.main())
  