### 4.a. 安裝/修改
#### 安裝
cellInfoMonitor 的安裝檔放 cellInfoMonitor 資料夾中的 `app\build\outputs\apk\debug` 路徑。

安裝後須先允許應用程式的權限。


#### 修改
完整的原始程式存放在名為 cellInfoMonitor 的 project 資料夾中。如果需要更改原始程式，則需要先安裝 visual studio 再進行修改。

主要檔案為資料夾中的

a. `\app\src\main\java\com\example\cellinfomonitor\MainActivity.java` (主要函式、邏輯判斷)

b. `\app\src\main\res\layout\activity_main.xml` (手機螢幕上按鈕、文字的位置、排版)

c. `\app\src\main\AndroidManifest.xml` (權限相關)

如欲透過 USB cable 在手機上安裝修改後的 project，則手機須先開啟開發者模式並 enable USB偵錯、USB安裝等權限。



### 4.b. 操作流程
在應用程式中有三個按鈕，分別為 start，record，以及 stop。

一、實驗開始時，須先按 start 鍵使程式開始運作，此時 cellInfoMonitor 應會顯示目前量測到的相關資訊
二、欲開始記錄資訊時(實驗開始時)，再按下 record 鍵開始記錄資訊
三、而當要停止實驗時，則需按下 stop 鍵以讓程式停止運作

```
a. 此應用程式在跳出程式到主螢幕後都仍可以繼續在背景執行，但是執行一段時間後會自動停止。因此，如果要保證應用程式持續運行，仍建議應用程式維持在手機畫面上(可以在按下 start 鍵前使用螢幕分割)
b. 實驗過程中應用程式的更新速度可能因為手機負載而變慢。手機重新開機後便可恢復正常。
c. 只要按下 record 鍵，檔案就會⽣成，無論是按下 stop 主動停⽌，還是因意外⾃動停⽌，都會保存下直到停⽌前的記錄資訊。
```
