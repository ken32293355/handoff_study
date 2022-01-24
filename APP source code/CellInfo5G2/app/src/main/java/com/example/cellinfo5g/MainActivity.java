/*
================CellInfo5G================
This Project can save the information of the cell phone and the serving cells.
For faster data collecting rate, this application doesn't show information on the screen;
This application also doesn't collect GPS information and other neighboring cell information

The information types contains:
    Date (Timestamp)
    Receiving Rate,Transmitting Rate of the cell phone (Bytes/s)
    Downstream/Upstream bandwidth (Kbps)
    RSRP/RSRQ of serving lte cell
    SS_RSRP/SS_RSRQ of serving nr cell
    MNC,MCC,CID,PCI of serving cell
    band,earfcn of serving cell
    PCI, RSRP, RSRQ, earfcn of neighboring cell (can catch LTE neighbor cell only)
*/

package com.example.cellinfo5g;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.Manifest;
import android.app.AlertDialog;
import android.content.Context;
import android.content.ContextWrapper;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.Criteria;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.net.ConnectivityManager;
import android.net.NetworkCapabilities;
import android.net.NetworkInfo;
import android.net.TrafficStats;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.os.StrictMode;
import android.telephony.CellIdentity;
import android.telephony.CellIdentityLte;
import android.telephony.CellIdentityNr;
import android.telephony.CellInfo;
import android.telephony.CellInfoCdma;
import android.telephony.CellInfoGsm;
import android.telephony.CellInfoLte;
import android.telephony.CellInfoNr;
import android.telephony.CellInfoTdscdma;
import android.telephony.CellInfoWcdma;
import android.telephony.CellSignalStrength;
import android.telephony.CellSignalStrengthLte;
import android.telephony.CellSignalStrengthNr;
import android.telephony.PhoneStateListener;
import android.telephony.TelephonyDisplayInfo;
import android.telephony.TelephonyManager;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.Method;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;


import static android.telephony.CellInfo.CONNECTION_PRIMARY_SERVING;

public class MainActivity extends AppCompatActivity {
    //PhysicalChannelConfig
    private static String phonestate = "";
    int start = 0;
    int record = 0;

    private Button btn1;
    private Button btn2;
    private Button btn3;
    private TextView textView1;
    private TextView textView3;
    Calendar mCalendar;
    DateFormat df = new SimpleDateFormat("MM/dd/yy HH:mm:ss.SSS ");
    DateFormat df2 = new SimpleDateFormat("MMddyyhhmmss");

    LocationManager mLocationManager;
    LocationListener mLocationListener;

    ConnectivityManager connectivityManager;

    private long mStartRX = 0;
    private long mStartTX = 0;

    private TelephonyManager TM;
    int isNR;

    private List<CellInfo> CellInfoList;
    private CountDownLatch countDownLatch;
    private PhoneStateListener phoneStateListener;

    ExecutorService singleThreadExecutor = Executors.newSingleThreadExecutor();

    //螢幕左半部顯示之各行名稱; csv file 中的 column names。之後的 columns 分別存取 neighboring cell 的 PCI, RSRP, RSRQ, earfcn
    String names = "Date,RxRate,TxRate,DLBandwidth,ULBandwidth,MNC,MCC,CID,PCI,LTE_RSRP,LTE_RSRQ,NR_SSRSRP,NR_SSRSRQ,earfcn";

    FileOutputStream fos;
    File fileLocation;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        btn1 = findViewById(R.id.button);
        btn2 = findViewById(R.id.button2);
        btn3 = findViewById(R.id.button3);
        textView1 = findViewById(R.id.textView2);
        textView3 = findViewById(R.id.textView3);
        textView3.setText(names.replace(",", "\n"));

        TM = (TelephonyManager) getSystemService(TELEPHONY_SERVICE);
        Context context = this;
        System.out.println(ContextCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_FINE_LOCATION));
        System.out.println(ContextCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_COARSE_LOCATION));


        //textView1.setText(String.valueOf(time).concat(" time ").concat(df.format(mCalendar.getTime())));
        //------------------measure bandwidth
        mStartRX = TrafficStats.getTotalRxBytes();
        mStartTX = TrafficStats.getTotalTxBytes();
        if (mStartRX == TrafficStats.UNSUPPORTED || mStartTX == TrafficStats.UNSUPPORTED) {
            AlertDialog.Builder alert = new AlertDialog.Builder(this);
            alert.setTitle("Uh Oh!");
            alert.setMessage("Your device does not support traffic stat monitoring.");
            alert.show();
        }



        Handler handler = new Handler();
        Runnable runnable = new Runnable() {
            @RequiresApi(api = Build.VERSION_CODES.R)
            @Override
            public void run() {
                //----------------time related setting----------------
                mCalendar = Calendar.getInstance();
                String showStr = df.format(mCalendar.getTime());


                if (ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                        || ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED
                        || ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_BACKGROUND_LOCATION) == PackageManager.PERMISSION_GRANTED) {

                    System.out.println(ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_FINE_LOCATION));
                    System.out.println(ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_COARSE_LOCATION));
                    System.out.println(ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_BACKGROUND_LOCATION));


                    //----------------get measured bytes info and rx/tx Bytes----------------
                    long rxBytes = TrafficStats.getTotalRxBytes() - mStartRX;
                    showStr = showStr.concat(",").concat(Long.toString(rxBytes));
                    long txBytes = TrafficStats.getTotalTxBytes() - mStartTX;
                    showStr = showStr.concat(",").concat(Long.toString(txBytes));


                    mStartRX = TrafficStats.getTotalRxBytes();	//getTotalRxBytes() 值會累加，每一秒的值減去上一秒的值即為每秒的 rx tx bytes
                    mStartTX = TrafficStats.getTotalTxBytes();

                    System.out.println(rxBytes);
                    System.out.println(txBytes);
                    System.out.println("gogogo");

                    //----------------get DL and UL bandwidth info----------------

                    NetworkCapabilities nc = connectivityManager.getNetworkCapabilities(connectivityManager.getActiveNetwork());
                    if (nc != null) {
                        showStr = showStr.concat(",").concat(String.valueOf(nc.getLinkDownstreamBandwidthKbps()));
                        showStr = showStr.concat(",").concat(String.valueOf(nc.getLinkUpstreamBandwidthKbps()));
                    } else {
                        showStr = showStr.concat(",-");
                        showStr = showStr.concat(",-");
                    }

                    //----------------get cell info----------------
                    CellInfoList = TM.getAllCellInfo();
                    if (CellInfoList == null) {
                        System.out.println("getAllCellInfo is null");
                        showStr = showStr.concat(",Disconnected");
                    } else {
                        System.out.println("getAllCellInfo is not null");
                    }

                    int num_of_registered = 0;
                    String showStr2 = "", showStr3 = "";	//showStr2: cellinfo of registered cell; showStr3: cellinfo of neighboring cell

                    //1. 只有 serving cell 有 band 的資訊，因此第 2, 4 部分的 if-else statement 判斷中刪去 band 的紀錄; 但 neighbor cell 的 band 可以在後續處理時以 carrier number 做對應而得出
                    //      getBands() 只在 Android 11 可用
                    //2. 因為為 NSA 架構， all cells in CellInfoList 都是 lte type (cellInfo instanceof CellInfoLte == true)。第 3, 4 部分的 if-else statement 不會為 true
                    for (CellInfo cellInfo : CellInfoList) {

                        //LTE case
                        if (cellInfo.isRegistered() && cellInfo instanceof CellInfoLte && isNR == 0) {
                            num_of_registered += 1;

                            CellInfoLte LteInfo = (CellInfoLte) cellInfo;
                            CellIdentityLte cellIdentityLte = LteInfo.getCellIdentity();
                            showStr2 = showStr2.concat(",").concat(cellIdentityLte.getMncString());
                            showStr2 = showStr2.concat(",").concat(cellIdentityLte.getMccString());
                            showStr2 = showStr2.concat(",").concat(String.valueOf(cellIdentityLte.getCi()));
                            showStr2 = showStr2.concat(",").concat(String.valueOf(cellIdentityLte.getPci()));

                            showStr2 = showStr2.concat(",").concat(String.valueOf(LteInfo.getCellSignalStrength().getRsrp()));
                            showStr2 = showStr2.concat(",").concat(String.valueOf(LteInfo.getCellSignalStrength().getRsrq()));

                            // band information (only available in Android 11)
                            //showStr2 = showStr2.concat(", ");
                            //for (int band: cellIdentityLte.getBands())
                            //    showStr2 = showStr2.concat(String.valueOf(band)).concat(" ");
                            //showStr2 = showStr2.concat("band");
                            int checkNR = 0;
                            for (CellSignalStrength cellSignalStrength: TM.getSignalStrength().getCellSignalStrengths())
                            {
                                /*
                                if (cellSignalStrength instanceof CellSignalStrengthLte)
                                {
                                    showStr2 = showStr2.concat(",LTE");
                                    showStr2 = showStr2.concat(",").concat(String.valueOf(((CellSignalStrengthLte) cellSignalStrength).getRsrp()));
                                    showStr2 = showStr2.concat(",").concat(String.valueOf(((CellSignalStrengthLte) cellSignalStrength).getRsrq()));
                                }
                                 */
                                if (cellSignalStrength instanceof CellSignalStrengthNr)
                                {
                                    checkNR = 1;
                                    showStr2 = showStr2.concat(",").concat(String.valueOf(((CellSignalStrengthNr) cellSignalStrength).getSsRsrp()));
                                    showStr2 = showStr2.concat(",").concat(String.valueOf(((CellSignalStrengthNr) cellSignalStrength).getSsRsrq()));
                                    //CSi RSRP, RSRQ function always return dummy value (2147483647)
                                    //showStr2 = showStr2.concat(",").concat(String.valueOf(((CellSignalStrengthNr) cellSignalStrength).getCsiRsrp()));
                                    //showStr2 = showStr2.concat(",").concat(String.valueOf(((CellSignalStrengthNr) cellSignalStrength).getCsiRsrq()));
                                }
                            }
                            if(checkNR == 0)
                                showStr2 = showStr2.concat(",-,-");

                            showStr2 = showStr2.concat(",").concat(String.valueOf(cellIdentityLte.getEarfcn()));

                            break;

                        }
                        else if (cellInfo instanceof CellInfoLte && isNR == 0) {
                            CellInfoLte LteInfo = (CellInfoLte) cellInfo;
                            CellIdentityLte cellIdentityLte = LteInfo.getCellIdentity();
                            showStr3 = showStr3.concat(",").concat(String.valueOf(cellIdentityLte.getPci()));

                            showStr3 = showStr3.concat(",").concat(String.valueOf(LteInfo.getCellSignalStrength().getRsrp()));
                            showStr3 = showStr3.concat(",").concat(String.valueOf(LteInfo.getCellSignalStrength().getRsrq()));

                            showStr3 = showStr3.concat(",").concat(String.valueOf(cellIdentityLte.getEarfcn()));

                            break;
                        }

                        //NR case
                        else if (cellInfo.isRegistered() && cellInfo instanceof CellInfoLte && isNR == 1)
                        {
                            num_of_registered += 1;
                            CellInfoLte NRInfo = (CellInfoLte) cellInfo; //avoid wrong casting......
                            CellIdentityLte cellIdentityNR = (CellIdentityLte) NRInfo.getCellIdentity();
                            showStr2 = showStr2.concat(",").concat(cellIdentityNR.getMncString());
                            showStr2 = showStr2.concat(",").concat(cellIdentityNR.getMccString());
                            showStr2 = showStr2.concat(",").concat(String.valueOf(cellIdentityNR.getCi()));
                            showStr2 = showStr2.concat(",").concat(String.valueOf(cellIdentityNR.getPci()));

                            showStr2 = showStr2.concat(",").concat(String.valueOf(NRInfo.getCellSignalStrength().getRsrp()));
                            showStr2 = showStr2.concat(",").concat(String.valueOf(NRInfo.getCellSignalStrength().getRsrq()));

                            // band information (only available in Android 11)
                            //showStr2 = showStr2.concat(", ");
                            //for (int band: cellIdentityNR.getBands())
                            //    showStr2 = showStr2.concat(String.valueOf(band)).concat(" ");
                            //showStr2 = showStr2.concat("band");

                            showStr2 = showStr2.concat(", ").concat(String.valueOf(cellIdentityNR.getEarfcn()));

                            break;
                        }
                        else if (cellInfo instanceof CellInfoLte && isNR == 1)
                        {
                            CellInfoLte NRInfo = (CellInfoLte) cellInfo; //avoid wrong casting......
                            CellIdentityLte cellIdentityNR = (CellIdentityLte) NRInfo.getCellIdentity();
                            showStr3 = showStr3.concat(",").concat(String.valueOf(cellIdentityNR.getPci()));

                            showStr3 = showStr3.concat(",").concat(String.valueOf(NRInfo.getCellSignalStrength().getRsrp()));
                            showStr3 = showStr3.concat(",").concat(String.valueOf(NRInfo.getCellSignalStrength().getRsrq()));

                            showStr3 = showStr3.concat(", ").concat(String.valueOf(cellIdentityNR.getEarfcn()));

                            break;
                        }
                        else if (cellInfo.isRegistered() && cellInfo instanceof CellInfoWcdma) {
                            //------------fallback to 3G-----------
                            showStr = showStr.concat(",fallback to wcdma");
                        }
                        else
                        {
                            //------------基本不會進入這裡，只是萬一出現就印一下 來debug-------------
                            System.out.println("handsome handsome so handsome 0127debug");
                            System.out.println(isNR);
                            System.out.println(cellInfo.isRegistered());
                            System.out.println(cellInfo instanceof CellInfoLte);
                            System.out.println(cellInfo instanceof CellInfoNr);
                            System.out.println(cellInfo instanceof CellInfoTdscdma);
                            System.out.println(cellInfo instanceof CellInfoGsm);
                            System.out.println(cellInfo instanceof CellInfoCdma);
                            System.out.println("handsome handsome so handsome 0127debug2");
                        }
                    }


                    //------------------update the cellinfo in cache every second-----------------------
                    countDownLatch = new CountDownLatch(1);
                    TM.requestCellInfoUpdate(singleThreadExecutor,new TelephonyManager.CellInfoCallback()
                            {
                                @Override
                                public void onCellInfo(@NonNull List<CellInfo> cellInfo) {
                                    System.out.println("update successfully");
                                    countDownLatch.countDown();
                                    System.out.println("0125debug1");
                                    System.out.println(countDownLatch.getCount());
                                }

                                @Override
                                public void onError(int errorCode, @Nullable Throwable detail) {
                                    super.onError(errorCode, detail);
                                    System.out.println("not update successfully");
                                    countDownLatch.countDown();
                                }
                            }
                    );
                    try {
                        System.out.println("0125debug2");
                        System.out.println(countDownLatch.getCount());
                        boolean result = countDownLatch.await(5000, TimeUnit.MILLISECONDS);
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }

                    //-------------Combine all the information--------------
                    showStr = showStr.concat(showStr2).concat(showStr3);
                    if (num_of_registered > 1){	//基本不會進入這裡，只是萬一出現就印一下來debug
                        String warning = ",Warning: more than one cell registered!!!";
                        showStr = warning.concat(showStr);
                    }
                    showStr = showStr.concat("\n");

                    //-------------有按下 record button, 將其輸入檔案中----------
                    if (record == 1){
                        try {
                            fos.write(showStr.getBytes());
                        } catch (FileNotFoundException e) {
                            e.printStackTrace();
                        } catch (IOException e) {
                            e.printStackTrace();
                            textView1.setText("Error");
                        }


                        textView1.setText("recording...");
                    }

                }

                handler.postDelayed(this, 5);
            }
        };

        //-------------------手機螢幕右上角的4G, 5G 狀態，但是不代表實際上是否真的有 5G connection---------------------
        //reference: GSMA 5GSI OMD default configuration
        //但仍保留以備不時之需
        phoneStateListener = new PhoneStateListener() {

            @RequiresApi(api = Build.VERSION_CODES.R)
            @Override
            public void onDisplayInfoChanged(TelephonyDisplayInfo telephonyDisplayInfo) {
                if (ActivityCompat.checkSelfPermission(context, Manifest.permission.READ_PHONE_STATE) != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{Manifest.permission.READ_PHONE_STATE}, 2000);
                }
                super.onDisplayInfoChanged(telephonyDisplayInfo);

                switch (telephonyDisplayInfo.getOverrideNetworkType()) {
                    case TelephonyDisplayInfo.OVERRIDE_NETWORK_TYPE_LTE_ADVANCED_PRO:
                        isNR = 1;
                        break;
                    case TelephonyDisplayInfo.OVERRIDE_NETWORK_TYPE_NR_NSA:
                        isNR = 1;
                        break;
                    case TelephonyDisplayInfo.OVERRIDE_NETWORK_TYPE_NR_NSA_MMWAVE:
                        isNR = 1;
                        break;

                    default:
                        isNR = 0;
                        break;
                }
                System.out.println("RRRRRRRRRRRRRRRRRRRRRRRRR");
                System.out.println(telephonyDisplayInfo.getOverrideNetworkType());
            }


        };

        //-----------按下 start button-----------
        btn1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // take some actions
                start = 1;
                textView1.setText(String.valueOf(start));

                //----------------gps location related setting
                if (ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                        || ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED
                        || ContextCompat.checkSelfPermission(context, android.Manifest.permission.ACCESS_BACKGROUND_LOCATION) == PackageManager.PERMISSION_GRANTED) {

                    mLocationListener = new LocationListener() {
                        @Override
                        public void onLocationChanged(@NonNull Location location) {

                        }
                    };
//                    mLocationManager = (LocationManager) getSystemService(LOCATION_SERVICE);
//                    mLocationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 0, 0, mLocationListener);

                    connectivityManager = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
                }

                handler.postDelayed(runnable, 5);
            }
        });

        //----------按下 stop button---------
        btn2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // take some actions
                start = 0;
                record = 0;

                handler.removeCallbacks(runnable);
                try {
                    fos.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
                textView1.setText("Recorded");
            }
        });

        //-----------按下 record button-----------
        btn3.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // take some actions
                record = 1;
                mCalendar = Calendar.getInstance();

                if (checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                        != PackageManager.PERMISSION_GRANTED) {
                    requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, 2000);
                }
                else{
                    System.out.println("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh");
                }


                StrictMode.VmPolicy.Builder builder = new StrictMode.VmPolicy.Builder();
                StrictMode.setVmPolicy(builder.build());
                builder.detectFileUriExposure();

                ContextWrapper cw = new ContextWrapper(getApplicationContext());
                File directory = cw.getExternalFilesDir(Environment.DIRECTORY_DOCUMENTS);
                fileLocation = new File(directory, df2.format(mCalendar.getTime()) + ".csv");
                try {

                    fos = new FileOutputStream(fileLocation, true);
                    String column_names;
                    column_names = names + '\n';
                    fos.write(column_names.getBytes());

                    System.out.println("yayaya");

                } catch (FileNotFoundException e) {
                    e.printStackTrace();
                } catch (IOException e) {
                    e.printStackTrace();
                    textView1.setText("Error");
                }


            }
        });
    }

}