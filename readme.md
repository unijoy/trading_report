## General 

dynamic call functions in *adapter* directory, the function name start with 'html_'
then generate the html report for quick exploration.

### entrypoint

```shell
pip install -r requirements.txt
python Dynamic_Report.py
```


### Directory description
```
.
├── adapter # dataframe and plot to html 
├── base # common utils
└── templates # html template
```

### custom guide
add any function you want to be called in adapter.   

function should return (html,title,res)

#### html 
pure html string, can generate from
```python
plotly.offline.plot(fig,include_plotlyjs=False,output_type='div')
# or
dataframe.to_html(classes="table table-hover table-bordered table-striped")
```
#### title
string of text as you wish

#### res
res represents the objects you want to pass through the dynamic chain as input parameters for later functions to use.

In current version,function order not yet considered.   
If a function depends on the return value of another function, it will be held until the latter function returns the necessary parameters.

