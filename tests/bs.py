from bs4 import BeautifulSoup

html_str = '''<div class="popup-body"><div class="content" style="height: auto;"><table border="0" class="infoTable">
<tbody><tr><td colspan="2" class="entityFont"><img src="https://logos.factiva.com/wc60145logo.gif" onerror="display:none" title="26th September (Yemen, Arabic Language)" border="0" alt="26th September (Yemen, Arabic Language)"></td></tr>
            <tr>               <td colspan="2" class="sourceListRow">                  <div id="sourceListLink" style="display: none;"><span id="sourceListToggle" title="此资讯来源出现在 [] 资讯来源列表。">资讯来源列表</span></div>                  <div id="sourceListNotFoundLabel" style="" title="此资讯来源出现在 0 资讯来源列表。">资讯来源列表 (0) |</div>                  <div id="saveSourceListLink" style="">                     <span id="saveSourceListToggleTitle" class="" title="">添加</span>                     <span id="saveSourceListToggle" class="slClose" title=""></span>                  </div>                  <div class="dt-divider" style="display:none"></div><div id="saveSourceListsPnl" class="head-sub" style="display:none;">      <form action="" method="post" data-hidecreateaddtolist="false" data-srclstnotfound="true">
        <div class="or-not-wrapper">
           <input id="excl-in-list" name="list-incl-excl" type="checkbox" value="not">
           <label for="not">在列表上添加为排除资料来源</label>
        </div>

        <div class="add-wrapper">

           <input checked="checked" id="add-to-list" name="list-select" type="radio" value="">
           <label for="add-to-list">添加到列表</label>
           <div class="report-options-wrapper report-in-wrapper">
               <span class="selected unselected ellipsis" title="default" listid="0">选择列表</span>
               <span class="fi-two fi_d-arrow-thick-drk-gray"></span>
               <div class="filter-wrapper">
                   <ul class="filter-list">
                   </ul>
               </div>
           </div>
        </div>
        <div class="create-wrapper">
              <input id="create-new-list" name="list-select" type="radio" value="create" checked="checked">
              <label for="create-new-list">创建新列表</label>
              <input class="list-title" maxlength="30" name="list-title" type="text" value="">
        </div>

        <div class="submit-wrapper">
              <div class="dj-list-item">
                <a class="dj_btn dj_btn-blue" href="javascript:void(0);" id="save-new-author-list">保存</a>
                <a class="dj_btn dj_btn-grey" href="javascript:void(0);" id="cancel-new-author-list">取消</a>
              </div>
        </div>
    </form>
    <div class="clearfix"></div>
</div>                  <div class="clear"></div>                  <div id="sourceListsPnl" style="display: none;">                     <div class="sourceListLbl">此资讯来源也被包括在这些列表中：</div><div class="sourceListDiv">                          <div class="personalSourceList" style="display: none;">                             <div class="personalSourceListTitle">个人资讯来源列表</div>                             <div class="personalSourceListContent"></div>                          </div>                          <div class="groupSourceList" style="display: none;">                             <div class="groupSourceListTitle">组资讯来源列表</div>                             <div class="groupSourceListContent"></div>      </div>                     </div>                     <div class="sourceListError" style="display: none;"></div>                 </div>                 <div class="hr-divider clear" style=""></div>              </td>          </tr>
<tr><td class="label">描述: </td>
<td class="value"><div class="sourceText">Online news from this weekly political newspaper published in Yemen. Country of origin: Yemen</div></td></tr>
<tr><td class="label">资讯来源代码: </td>
<td class="value">WC60145</td></tr>
<tr><td class="label">语言: </td>
<td class="value">阿拉伯语</td></tr>
<tr><td class="label">网址: </td>
<td class="value"><div class="sourceWebURL" onclick="NewWindow('http://www.26sep.net');return false;">http://www.26sep.net</div></td></tr>
<tr><td class="label">资讯来源内容包含范围: </td>
<td class="value">选择的内容包含范围</td></tr>
<tr><td class="label">频数: </td>
<td class="value">不定期</td></tr>
</tbody></table>
<table width="100%"><tbody><tr><td align="right">

</td></tr></tbody></table>
</div></div>
'''

def find_popup_field_value(html_str, key):
	key_val = key.strip()
	soup = BeautifulSoup(html_str)
	trs = soup.find_all('tr')
	rtn = None
	for idx, tr in enumerate(trs):
		if idx < 2:
			continue
		key_td = tr.contents[0]
		val_td = tr.contents[2]
		if key_td.text.strip() == key_val:
			rtn = val_td.div.text.strip() if val_td.div else val_td.text.strip()
			break
	return rtn

a = find_popup_field_value(html_str, '描述:')
b = find_popup_field_value(html_str, '资讯来源代码:')

soup = BeautifulSoup(html_str)
trs = soup.find_all('tr')
name = trs[0].find('img').title.strip()
c = 0