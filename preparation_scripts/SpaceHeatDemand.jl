# By David Ribo
using Pkg, JuMP, XLSX, DataFrames, DelimitedFiles, Dates
import XLSX, DataFrames, CSV, Dates

full_path = joinpath(pwd(),"data" , "weatherpotentialNetherlands" , "heating" ,"sh_corr.xlsx")
full_path_2 = joinpath(pwd(),"data" , "weatherpotentialNetherlands" , "heating" ,"weather_data.xlsx")
println(full_path_2)
SH_corr = XLSX.readdata(full_path, "sh_corr!B3:C26")
AS_corr = XLSX.readdata(full_path, "sh_corr!F3:G3")
GS_corr = XLSX.readdata(full_path, "sh_corr!J3:K3")
Temp = XLSX.readdata(full_path_2, "weather_data!B2:B350641")

#HD = DataFrame(T = [], HD = [])
HD_pred = zeros(length(Temp),4)
ii = 0
for i in 1:length(Temp)

    slope_AS = AS_corr[1]
    intercept_AS = AS_corr[2]
    slope_GS = GS_corr[1]
    intercept_GS = GS_corr[2]

    HD_pred[i,2] = intercept_AS + Temp[i]*slope_AS
    if HD_pred[i,2] > 4.06 
        HD_pred[i,2] = 4.06 
    end

    HD_pred[i,3] = intercept_GS + Temp[i]*slope_GS
    if HD_pred[i,3] > 6.32
        HD_pred[i,3] = 6.32 
    end
    if HD_pred[i,3] < 2.5
        HD_pred[i,3] = 2.5 
    end

    if ii == 24
        global ii = 0 
    end

    global ii = ii + 1 
        slope = SH_corr[ii,1]
        intercept = SH_corr[ii,2]


        HD_pred[i,1] = intercept + Temp[i]*slope
        if HD_pred[i,1] < 0 
            HD_pred[i,1] = 0
        end

end

#Market share per technology 
ASHP_MS = 0.6 
GSHP_MS = 0.4 

HD_pred[:,4] = GSHP_MS*HD_pred[:,1]./HD_pred[:,2] + ASHP_MS*HD_pred[:,1]./HD_pred[:,3]

HD = DataFrame(Temp=Temp[:], HD=HD_pred[:,1], AS=HD_pred[:,2], GS=HD_pred[:,3], FD=HD_pred[:,4])


CSV.write("SH_demand_corr.csv", HD)
#XLSX.writetable("SH_demand_corr.xlsx",HD = (DataFrames.collect(eachcol(HD)), DataFrames.names(HD)))


