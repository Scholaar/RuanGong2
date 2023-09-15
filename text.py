import tkinter as tk
import os
import re
import urllib.request,urllib.error
import time
import threading
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import shutil
import requests
import re
import urllib.parse
import tkinter as tk
from tkinter import Scrollbar, Listbox, messagebox
import json
import jsonpath

#将会在该文件的目录下创建data文件夹，用于存放爬取的题目

cookie = {
    '_uid': '1090190',
    '__client_id': '3dd0444c9266dd488bf50ef67baecef5b7ad3171',
    'C3VK': 'da01e2',
}

class MyCrawler1:
    def __init__(self, minn=1000, maxn=1050, text_output=None):
        self.baseUrl = "https://www.luogu.com.cn/problem/P"  # 基础URL
        self.base_TJ_Url = "https://www.luogu.com.cn/problem/solution/P"  # 基础题解URL
        self.savePath = "./data/"  # 修改保存路径为"data"文件夹
        self.minn = minn  # 最小题号
        self.maxn = maxn  # 最大题号
        self.text_output = text_output  # 文本框对象
        self.should_stop = False  # 停止标志位

    def run(self):
        
        if not os.path.exists(self.savePath):   # 如果不存在该文件夹则创建
            os.makedirs(self.savePath)
        
        print("计划爬取到P{}".format(self.maxn))
        self.text_output.insert(tk.END, '计划爬取到P{}\n'.format(self.maxn))
        self.text_output.see(tk.END)
        for i in range(self.minn,self.maxn+1):
            if self.should_stop:# 检查是否应该停止
                break
            time.sleep(1)
            print("正在爬取P{}...".format(i),end="")
            html = self.Get_HTML(self.baseUrl + str(i))
            html_TJ = self.Get_HTML(self.base_TJ_Url + str(i))
            if html == "error":
                print("爬取失败，可能是不存在该题或无权查看")
            else:
                problemMD = self.Get_MD(html)
                problemMD_TJ = self.Get_TJ_MD(html_TJ)
                title = self.Get_title(str(i))
                print("爬取成功！正在保存...",end="")
                if not os.path.exists(self.savePath+'P' + str(i) + '-' + str(title)):   # 如果不存在该文件夹则创建
                    os.makedirs(self.savePath+'P' + str(i) + '-' + str(title)+"/")
                    self.text_output.insert(tk.END, '已创建文件夹：P' + str(i) + '-' + str(title) + '\n')
                    self.text_output.see(tk.END)
                else:
                    print('文件夹已存在，无需创建！')
                    self.text_output.insert(tk.END, '文件夹已存在，无需创建！\n')
                    self.text_output.see(tk.END)
                self.saveData(problemMD,"P"+str(i)+"-"+title+".md",self.savePath+'P' + str(i) + '-' + str(title)+"/")
                self.saveData(problemMD_TJ,"P"+str(i)+"-"+title+"-题解.md",self.savePath+'P' + str(i) + '-' + str(title)+"/")
                print("保存成功!")
                if self.text_output is not None:
                    self.text_output.insert(tk.END, f'P{i}题目以及题解已经保存\n')
                    self.text_output.see(tk.END)
                    self.text_output.update_idletasks()  # 更新文本框内容
        if self.should_stop:
            print("已停止")
            self.text_output.insert(tk.END, '已停止\n')
            self.text_output.see(tk.END)
            self.should_stop = False
        else:
            print("爬取完毕")

    def stop(self):
        self.should_stop = True  # 设置停止标志位

    def Get_HTML(self,url):
        # 创建一个随机User-Agent生成器
        user_agent = UserAgent()
        # 设置请求头
        headers = {
            'User-Agent': user_agent.random,
        }
        
        session = requests.Session()
        
        for key in cookie:
            session.cookies[key]=cookie[key]
            
        # response = requests.get(url, headers=headers)
        response = session.get(url=url, headers=headers)
        # 继续处理响应内容
        return response.text

    def Get_MD(self,html):
        bs = BeautifulSoup(html, "html.parser")

        # 当网页中没有article标签时，重试
        core = bs.select("article")[0]
        md = str(core)
        md = re.sub("<h1>", "# ", md)
        md = re.sub("<h2>", "## ", md)
        md = re.sub("<h3>", "#### ", md)
        md = re.sub("</?[a-zA-Z]+[^<>]*>", "", md)
        return md
    
        # 创建标题获取函数
    def Get_title(self,problemID):
        # 生成要访问的url
        url = 'https://www.luogu.com.cn/problem/P' + str(problemID)
        print('----------- 正在爬取 ' + str(problemID) + ' ------------')
        self.text_output.insert(tk.END, '----------- 正在爬取 ' + str(problemID) + ' ------------\n')
        self.text_output.see(tk.END)
        # 创建一个随机User-Agent生成器
        user_agent = UserAgent()
        # 设置请求头
        headers = {
            'User-Agent': user_agent.random,
        }
        # 创建请求
        r = requests.get(url, headers=headers)
        # 获取网页内容
        soup = BeautifulSoup(r.text, 'html.parser')
        # 获取题目标题、去掉-前的部分和末尾空格
        title = soup.find('title').text.split('-')[0].strip()

        return title
    
    def Get_TJ_MD(self,html):
        soup = BeautifulSoup(html, "html.parser")
        # 获取script标签中的内容
        encoded_content = soup.find('script').text
        # 定位第一个"的位置，从当前开始截取
        start = encoded_content.find('"')
        # 定位第二个"的后面一个位置，到那里结束截取
        end = encoded_content.find('"', start + 1)
        # 截取出题解的内容
        encoded_content = encoded_content[start + 1:end]
        decoded_content = urllib.parse.unquote(encoded_content)
        decoded_content = decoded_content.encode('utf-8').decode('unicode_escape')
        # 从第一个"content":"后面开始截取
        start = decoded_content.find('"content":"')
        # 从第一个'","type":"题解"'前面结束截取
        end = decoded_content.find('","type":"题解"')
        # 截取出题解的内容
        decoded_content = decoded_content[start + 11:end]
        return decoded_content

    def saveData(self, data,filename,Path):
        cfilename = Path + filename
        file = open(cfilename,"w",encoding="utf-8")
        for d in data:
            file.writelines(d)  # 写入数据
        file.close()

# class MyCrawler2:
#     def __init__(self,text_output=None):
#         self.should_stop = False  # 停止标志位
#         self.text_output = text_output  # 文本框对象

#     def Get_info(self,anum = 1000, bnum = 1051):
#         user_agent = UserAgent()
#         headers = {
#             'User-Agent': user_agent.random,
#             "Cookie": "__client_id=3dd0444c9266dd488bf50ef67baecef5b7ad3171; _uid=1090190; C3VK=956222",
#         }
#         tag_url = 'https://www.luogu.com.cn/_lfe/tags'
#         tag_html = requests.get(url=tag_url, headers=headers).json()
#         tags_dicts = []
#         tags_tag = list(jsonpath.jsonpath(tag_html, '$.tags')[0])
#         for tag in tags_tag:
#             if jsonpath.jsonpath(tag, '$.type')[0] != 1 or jsonpath.jsonpath(tag, '$.type')[0] != 4 or \
#                     jsonpath.jsonpath(tag, '$.type')[0] != 3:
#                 tags_dicts.append({'id': jsonpath.jsonpath(tag, '$.id')[0], 'name': jsonpath.jsonpath(tag, '$.name')[0]})

#         arr = ['暂无评定', '入门', '普及−', '普及/提高−', '普及+/提高', '提高+/省选−', '省选/NOI−', 'NOI/NOI+/CTSC']
#         ts = []

#         page = 1
#         url = f'https://www.luogu.com.cn/problem/list?page={page}'
#         html = requests.get(url=url, headers=headers).text
#         urlParse = re.findall('decodeURIComponent\((.*?)\)\)', html)[0]
#         htmlParse = json.loads(urllib.parse.unquote(urlParse)[1:-1])
#         result = list(jsonpath.jsonpath(htmlParse, '$.currentData.problems.result')[0])

#         for res in result:
#             pid = jsonpath.jsonpath(res, '$.pid')[0]

#             # 定义ppid,将pid中的P去掉
#             ppid = pid[1:]

#             # 当pid小于anum时，跳过本次循环
#             if int(ppid) < anum:
#                 continue

#             # 当pid大于bnum时，跳出循环
#             if int(ppid) > bnum:
#                 break

#             title = jsonpath.jsonpath(res, '$.title')[0]
#             difficulty = arr[int(jsonpath.jsonpath(res, '$.difficulty')[0])]
#             tags_s = list(jsonpath.jsonpath(res, '$.tags')[0])
#             tags = []
#             for ta in tags_s:
#                 for tags_dict in tags_dicts:
#                     if tags_dict.get('id') == ta:
#                         tags.append(tags_dict.get('name'))
#             wen = {
#                 "题号": pid,
#                 "题目": title,
#                 "标签": tags,
#                 "难度": difficulty
#             }
#             ts.append(wen)
#         # 将数据写入JSON文件
#         with open('info.json', 'w', encoding='utf-8') as f:
#             json.dump(ts, f, ensure_ascii=False, indent=4)
            
#         print("info爬取成功！")
#         self.text_output.after(0, lambda: self.text_output.insert(tk.END, 'info已获取\n'))
#         self.text_output.after(0, lambda: self.text_output.see(tk.END))


#     def stop(self):
#         self.should_stop = True  # 设置停止标志位

class MyGUI:
    def __init__(self):
        # 创建主窗口
        self.window = tk.Tk()
        self.window.title('爬爬爬爬爬')  # 窗口标题
        self.window.geometry('500x300')  # 窗口大小

        # 创建2个Frame，左边的用于放置按钮，右边的用于放置文本框
        self.frame_left = tk.Frame(self.window)
        self.frame_left.pack(side=tk.LEFT)
        
        self.frame_right = tk.Frame(self.window)
        self.frame_right.pack(side=tk.RIGHT)
        
        # 创建5个按钮
        self.button_reptile = tk.Button(self.frame_left, text='爬虫', command=self.button_reptile_clicked)
        self.button_reptile.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.button_delete_data = tk.Button(self.frame_left, text='删除data文件夹', command=self.button_delete_data_clicked)
        self.button_delete_data.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # self.button_delete_info = tk.Button(self.frame_left, text='删除info', command=self.button_delete_info_clicked)
        # self.button_delete_info.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.button_empty_text = tk.Button(self.frame_left, text='清空文本框', command=self.button_empty_text_clicked)
        self.button_empty_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.button_search = tk.Button(self.frame_left, text='查找', command=self.button_search_clicked)
        self.button_search.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 创建一个文本框
        self.text = tk.Text(self.frame_right)
        self.text.pack()
        
        #爬虫类
        self.my_crawler1 = MyCrawler1(text_output=self.text)
        # self.my_crawler2 = MyCrawler2(text_output=self.text)

    def button_reptile_clicked(self):
        # 清空主窗口的内容
        for widget in self.window.winfo_children():
            widget.destroy()

        # 在主窗口中添加新的控件
        frame_left = tk.Frame(self.window)
        frame_left.pack(side=tk.LEFT)
        
        frame_right = tk.Frame(self.window)
        frame_right.pack(side=tk.RIGHT)
        
        # new_button_get_info = tk.Button(frame_left, text='获取Info', command=self.run_crawler2)
        # new_button_get_info.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        new_button_reptile_star = tk.Button(frame_left, text='开始爬虫', command=self.run_crawler1)
        new_button_reptile_star.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        new_button_stop_thread = tk.Button(frame_left, text='停止线程', command=self.button_stop_thread_clicked)
        new_button_stop_thread.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        new_button_empty_text = tk.Button(frame_left, text='清空文本框', command=self.clear_text)
        new_button_empty_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        new_button_return = tk.Button(frame_left, text='返回', command=self.return_to_main)
        new_button_return.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        new_text = tk.Text(frame_right)
        new_text.pack()

        # 更新爬虫类的文本框对象为新界面的文本框
        self.my_crawler1.text_output = new_text

    def return_to_main(self):
        # 清空主窗口的内容
        for widget in self.window.winfo_children():
            widget.destroy()
            
        self.window.geometry('500x300')

        # 在主窗口中重新添加原来的控件
        # 创建2个Frame，左边的用于放置按钮，右边的用于放置文本框
        self.frame_left = tk.Frame(self.window)
        self.frame_left.pack(side=tk.LEFT)
        
        self.frame_right = tk.Frame(self.window)
        self.frame_right.pack(side=tk.RIGHT)
        
        # 创建5个按钮
        self.button_reptile = tk.Button(self.frame_left, text='爬虫', command=self.button_reptile_clicked)
        self.button_reptile.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.button_delete_data = tk.Button(self.frame_left, text='删除data文件夹', command=self.button_delete_data_clicked)
        self.button_delete_data.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # self.button_delete_info = tk.Button(self.frame_left, text='删除info', command=self.button_delete_info_clicked)
        # self.button_delete_info.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.button_empty_text = tk.Button(self.frame_left, text='清空文本框', command=self.button_empty_text_clicked)
        self.button_empty_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.button_search = tk.Button(self.frame_left, text='查找', command=self.button_search_clicked)
        self.button_search.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 创建一个文本框
        self.text = tk.Text(self.frame_right)
        self.text.pack()

         # 更新爬虫类的文本框对象为主界面的文本框
        self.my_crawler1.text_output = self.text
        self.my_crawler2.text_output = self.text
    
    def run_crawler1(self):
        threading.Thread(target=self.my_crawler1.run).start()  # 在新线程中运行爬虫类
        
    # def run_crawler2(self):
    #     threading.Thread(target=self.my_crawler2.Get_info).start()  # 在新线程中运行爬虫类
        
         
    def clear_text(self):
        self.new_text.delete(1.0, 'end')  # 清空界面2的文本框内容

    def button_delete_data_clicked(self):
        # 删除"data"文件夹及其内部的所有文件
        if os.path.exists(self.my_crawler1.savePath):
            shutil.rmtree(self.my_crawler1.savePath)
        self.text.insert(tk.END, 'data文件及已删除\n')
        self.text.see(tk.END)
            
    # def button_delete_info_clicked(self):
    #     #删除info.json文件
    #     info_json_path = "./info.json"
    #     if os.path.exists(info_json_path):
    #         os.remove(info_json_path)
    #     self.text.insert(tk.END, 'json文件已删除\n')
    #     self.text.see(tk.END)
        
    def button_empty_text_clicked(self):
        self.text.delete(1.0, 'end')  # 清空文本框内容
        
    def button_search_clicked(self):      #新界面2
        # 清空主窗口的内容
        for widget in self.window.winfo_children():
            widget.destroy()
            
        #设置窗口大小
        self.window.geometry('300x600')

            # 创建子页面2
        page2_frame = tk.Frame()
        page2_frame.grid(row=0, column=0, sticky="nsew")

        # 在数据管理界面上添加返回首页按钮
        back_to_main_page2 = tk.Button(page2_frame, text="返回", command=self.return_to_main)
        back_to_main_page2.grid(row=0, column=0, pady=10)

        # 创建一个 LabelFrame 来组织难度和标签选择框
        filter_frame = tk.LabelFrame(page2_frame, text="筛选条件")
        filter_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nw")

        # 创建难度选择框
        difficulty_label = tk.Label(filter_frame, text="选择题目难度:")
        difficulty_label.grid(row=0, column=0, padx=5, pady=5)
        difficulty_var = tk.StringVar()
        difficulty_var.set("None")  # 默认值
        difficulty_option = tk.OptionMenu(filter_frame, difficulty_var, "暂无评定", "入门", "普及−", "普及/提高−","普及+/提高", "提高+/省选−", "省选/NOI−", "NOI/NOI+/CTSC")
        difficulty_option.grid(row=0, column=1, padx=5, pady=5)

        # 创建标签多选框和滚动条
        source_label = tk.Label(filter_frame, text="选择标签:")
        source_label.grid(row=1, column=0, padx=5, pady=5)

        source_scrollbar = Scrollbar(filter_frame, orient=tk.VERTICAL)
        source_scrollbar.grid(row=1, column=2, pady=5, sticky="ns")

        source_listbox = Listbox(filter_frame, selectmode=tk.MULTIPLE, yscrollcommand=source_scrollbar.set)
        source_listbox.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # 获取标签选项并将其添加到 Listbox 中
        source_options = self.get_tags_from_json()
        for option in source_options:
            source_listbox.insert(tk.END, option)

        source_scrollbar.config(command=source_listbox.yview)
        
        # 结果显示区域
        result_text = tk.Text(page2_frame, wrap=tk.WORD, width=40, height=10)
        result_text.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
        
        # 获取用户选择的标签选项
        selected_tags_indices = source_listbox.curselection()
        selected_tags = [source_options[i] for i in selected_tags_indices]

        # 获取用户选择的难度、标签和关键词
        selected_difficulty = difficulty_var.get()
        
        # self.my_crawler2.text_output = result_text

        def rearch():
            
            # 从 info.json 文件中读取题目数据
            def load_problem_data():
                try:
                    with open('.info.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        return data
                except FileNotFoundError:
                    return []
            
            datas = load_problem_data()
            
            found = False
            
            for data in datas:
                difficulty = (selected_tags == "None") or (selected_difficulty == data["难度"])
                tags = (not selected_tags) or (any(tag in selected_tags for tag in data["标签"]))

                # 如果所有条件匹配，将题目信息添加到结果中
                if difficulty and tags:
                    result_text.insert(tk.END,f"题号：{data['题号']}\n题目：{data['题目']}\n难度：{data['难度']}\n标签：{', '.join(data['标签'])}\n\n")
                    found = True  # 找到匹配的题目

            # 如果未找到内容，弹出提示框，并将所有选择清空
            if not found:
                messagebox.showinfo("未找到", "未找到匹配的题目。")
                # 清空选择
                difficulty_var.set("None")
                source_listbox.selection_clear(0, tk.END)  # 清除标签多选框的选择
                
        # 搜索按钮
        search_button = tk.Button(page2_frame, text="搜索", command=rearch)
        search_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        return page2_frame
        
    # 从info.json文件中读取标签种类
    def get_tags_from_json(self):
        try:
            with open('info.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                tags_set = set()  # 使用集合来存储不同的标签
                for item in data:
                    tags_set.update(item['标签'])
                return list(tags_set)
        except FileNotFoundError:
            return []

    def button_stop_thread_clicked(self):
        self.my_crawler1.stop()  # 停止爬虫类的运行
        self.my_crawler2.stop()  # 停止爬虫类的运行
    
    def __del__(self):
        self.my_crawler1.stop()  # 关闭GUI界面后停止爬虫类的运行
        
    def run(self):
        # 运行主循环
        self.window.mainloop()

def main():
    gui = MyGUI()
    gui.run()

if __name__ == "__main__":
    main()
