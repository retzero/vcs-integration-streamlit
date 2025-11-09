# Svcs-integration-streamlit

https://github.com/szeyu/streamlit-authentication-template/tree/main#



sudo apt install libpq-dev python3.12-dev


- For tree view, css change;

`.venv/lib/python3.12/site-packages/streamlit_tree_select/frontend/build/react-checkbox-tree.css`

```diff
.rct-title {
  padding: 0 5px;
  vertical-align: middle;
  flex-direction: row;
  -webkit-box-align: center;
  align-items: center;
  font-family: "Source Sans Pro", sans-serif;
  color: rgb(49, 51, 63);
+ width: 100%;
+ text-align-last: justify;
+ border-style: dashed;
+ border-width: 0px;
+ border-bottom-width: 1px;
+ border-color: #aed2e2;
}
```