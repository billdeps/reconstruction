import os, math, optparse, ROOT
from array import array

ROOT.gStyle.SetOptStat(111111)
ROOT.gROOT.SetBatch(True)

fe_integral_rescale = 0.1
cosm_rate_calib = [0.75,0.02] # central value, stat error

def doLegend(histos,labels,styles,corner="TR",textSize=0.035,legWidth=0.18,legBorder=False,nColumns=1):
    nentries = len(histos)
    (x1,y1,x2,y2) = (.85-legWidth, .7 - textSize*max(nentries-3,0), .90, .91)
    if corner == "TR":
        (x1,y1,x2,y2) = (.85-legWidth, .7 - textSize*max(nentries-3,0), .90, .91)
    elif corner == "TC":
        (x1,y1,x2,y2) = (.5, .75 - textSize*max(nentries-3,0), .5+legWidth, .91)
    elif corner == "TL":
        (x1,y1,x2,y2) = (.2, .75 - textSize*max(nentries-3,0), .2+legWidth, .91)
    elif corner == "BR":
        (x1,y1,x2,y2) = (.85-legWidth, .33 + textSize*max(nentries-3,0), .90, .15)
    elif corner == "BC":
        (x1,y1,x2,y2) = (.5, .33 + textSize*max(nentries-3,0), .5+legWidth, .35)
    elif corner == "BL":
        (x1,y1,x2,y2) = (.2, .33 + textSize*max(nentries-3,0), .33+legWidth, .35)
    leg = ROOT.TLegend(x1,y1,x2,y2)
    leg.SetNColumns(nColumns)
    leg.SetFillColor(0)
    leg.SetFillColorAlpha(0,0.6)  # should make the legend semitransparent (second number is 0 for fully transparent, 1 for full opaque)
    #leg.SetFillStyle(0) # transparent legend, so it will not cover plots (markers of legend entries will cover it unless one changes the histogram FillStyle, but this has other effects on color, so better not touching the FillStyle)
    leg.SetShadowColor(0)
    if not legBorder:
        leg.SetLineColor(0)
        leg.SetBorderSize(0)  # remove border  (otherwise it is drawn with a white line, visible if it overlaps with plots
    leg.SetTextFont(42)
    leg.SetTextSize(textSize)
    for (plot,label,style) in zip(histos,labels,styles): leg.AddEntry(plot,label,style)
    leg.Draw()
    ## assign it to a global variable so it's not deleted
    global legend_
    legend_ = leg
    return leg


def plotDensity():
    tf = ROOT.TFile('reco_run815.root')
    tree = tf.Get('Events')

    histos = []
    colors = [ROOT.kRed,ROOT.kBlue,ROOT.kOrange]
    #histo = ROOT.TH1F('density','',70,0,2500)
    histo = ROOT.TH1F('density','',70,0,20)
    for it in range(1,4):
        h = histo.Clone('h_iter{it}'.format(it=it))
        h.Sumw2()
        #tree.Draw('track_integral/track_nhits>>h_iter{it}'.format(it=it),'track_iteration=={it}'.format(it=it))
        #tree.Draw('track_integral/track_length>>h_iter{it}'.format(it=it),'track_iteration=={it}'.format(it=it))
        tree.Draw('track_length>>h_iter{it}'.format(it=it),'track_iteration=={it}'.format(it=it))
        h.Scale(1./h.Integral())
        h.SetFillColor(colors[it-1])
        h.SetLineColor(colors[it-1])
        h.SetFillStyle(3005)
        histos.append(h)


    # legend
    (x1,y1,x2,y2) = (0.7, .70, .9, .87)
    leg = ROOT.TLegend(x1,y1,x2,y2)
    leg.SetFillColor(0)
    leg.SetFillColorAlpha(0,0.6)
    leg.SetShadowColor(0)
    leg.SetLineColor(0)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    
    c = ROOT.TCanvas('c','',600,600)
    for ih,h in enumerate(histos):
        h.Draw('hist' if ih==0 else 'hist same')
        h.GetYaxis().SetRangeUser(0,0.25)
        h.GetXaxis().SetTitle('length (mm)')
        leg.AddEntry(h,'iteration {it}'.format(it=ih+1),'f')

    leg.Draw()

    c.SaveAs('density.pdf')


def plotNClusters(iteration=1):

    f = ROOT.TFile.Open('../runs/fng_runs.root')
    nclu_h = ROOT.TH1F('nclu_h','',20,0,80)
    
    for ie,event in enumerate(f.Events):
        #if event.run<46 or event.run>47: continue
        #if event.run<48 or event.run>50: continue
        if event.run<70 or event.run>71: continue
        nclu_it1 = 0
        for icl in range(event.nTrack):
            if event.track_nhits[icl]<100: continue
            if int(event.track_iteration[icl])>2: continue
            if math.hypot(event.track_xmean[icl]-1024,event.track_ymean[icl]-1024)>1000: continue
            #print "cluster x = ", event.track_xmean[icl]
            #print "cluster y = ", event.track_ymean[icl]
            nclu_it1 += 1
        nclu_h.Fill(nclu_it1)

    c = ROOT.TCanvas('c1','',600,400)
    nclu_h.SetLineColor(ROOT.kRed+2)
    nclu_h.SetMarkerColor(ROOT.kBlack)
    nclu_h.SetMarkerSize(1.5)
    nclu_h.SetMarkerStyle(ROOT.kOpenCircle)
    nclu_h.SetLineWidth(2)
    nclu_h.GetXaxis().SetTitle('# clusters / 100 ms')
    nclu_h.GetYaxis().SetTitle('Events')
    nclu_h.Draw('pe')
    nclu_h.Draw('hist same')
    c.SaveAs("nclusters_iter1_run70_71.pdf")

def withinFC(xmean,ymean,ax=400,ay=500,shape=2048):
    center = shape/2.
    x1 = xmean-center
    y1 = (ymean-center)*1.2
    return math.hypot(x1,y1)<ax

def withinFCFull(xmin,ymin,xmax,ymax,ax=400,ay=500,shape=2048):
    center = shape/2.
    x1 = xmin-center
    y1 = (ymin-center)*1.2
    x2 = xmax-center
    y2 = (ymax-center)*1.2
    return math.hypot(x1,y1)<ax and math.hypot(x2,y2)<ax

def slimnessCut(l,w,th=0.6):
    
        return (w/l)>th

def integralCut(i,minTh=1800,maxTh=3200):
    
        return (i>minTh) & (i<maxTh)
    
def varChoice(var):
    
    if var == 'integral':
        var1 = 'cl_integral'
        leg = 'Integral [ph]'
        histlimit = 6000
    elif var == 'length':
        var1 = 'cl_length*125E-3'
        leg = 'Length [mm]'
        histlimit = 32
    elif var == 'width':
        var1 = 'cl_width*125E-3'
        leg = 'Width [mm]'
        histlimit = 10
    elif var == 'size':
        var1 = 'cl_size'
        leg = 'Size [px]'
        histlimit = 1600
    elif var == 'slimness':
        var1 = 'cl_width/cl_length'
        leg = 'Slimness [w/l]'
        histlimit = 1.2
    else:
        exit()
    
    return var1, leg, histlimit
    

def fillSpectra(cluster='sc'):

    ret = {}
    #tf_ambe = ROOT.TFile('../runs/AmBeConfig/reco_runs_2317_to_2320_3D.root')
    tf_ambe  = ROOT.TFile('../runs/AmBeConfig/reco_runs_2097_to_2098_3D.root') ## 60/40
    ##tf_ambe =  ROOT.TFile('../runs/AmBeConfig/reco_ambe7030_3D.root') ## AmBe 70/30
    #tf_fe55 = ROOT.TFile('../runs/AmBeConfig/reco_runs_2252_to_2257_3D.root')
    #tf_fe55 = ROOT.TFile('../runs/AmBeConfig/reco_runs_2311_to_2313_3D.root')
    #tf_fe55 = ROOT.TFile('../runs/AmBeConfig/reco_runs_fe55_6040_3D.root') # many short runs
    tf_cosmics = ROOT.TFile('../runs/AmBeConfig/reco_runs_2156_to_2159_3D.root') ## cosmics run
    tf_fe55 = ROOT.TFile('../runs/AmBeConfig/reco_runs_Fe55.root')

    tfiles = {'fe':tf_fe55,'ambe':tf_ambe,'cosm':tf_cosmics}

    entries = {'fe': tf_fe55.Events.GetEntries(), 'ambe': tf_ambe.Events.GetEntries(), 'cosm': tf_cosmics.Events.GetEntries()}
    
    ## Fe55 region histograms
    ret[('ambe','integral')] = ROOT.TH1F("integral",'',50,0,1e4)
    ret[('ambe','integralExt')] = ROOT.TH1F("integralExt",'',200,0,50e4)
    ret[('ambe','length')]   = ROOT.TH1F("length",'',50,0,2000)
    ret[('ambe','width')]    = ROOT.TH1F("width",'',100,0,200)
    ret[('ambe','tgausssigma')]    = ROOT.TH1F("tgausssigma",'',100,0,40)
    ret[('ambe','nhits')]    = ROOT.TH1F("nhits",'',70,0,2000)
    ret[('ambe','slimness')] = ROOT.TH1F("slimness",'',50,0,1)
    ret[('ambe','density')]  = ROOT.TH1F("density",'',45,0,30)

    ## CMOS integral variables
    ret[('ambe','cmos_integral')] = ROOT.TH1F("cmos_integral",'',50,1.54e6,2.0e6)
    ret[('ambe','cmos_mean')]     = ROOT.TH1F("cmos_mean",'',50,0.36,0.56)
    ret[('ambe','cmos_rms')]      = ROOT.TH1F("cmos_rms",'',50,2,3)

    ## 2D vars
    ret[('ambe','integralvslength')] =  ROOT.TH2F("integralvslength",'',100,0,300,100,0,15e3)

    ret[('ambe','densityvslength')]      =  ROOT.TH2F("densityvslength",''     ,100,0,2000,45,0,30)
    ret[('ambe','densityvslength_zoom')] =  ROOT.TH2F("densityvslength_zoom",'',50,0,1000, 45,0,30)

    # ret[('fe','integralvslength')] = ROOT.TGraph()
    # ret[('fe','sigmavslength')] = ROOT.TGraph()
    # ret[('fe','sigmavsintegral')] = ROOT.TGraph()
    
    # x-axis titles
    titles = {'integral': 'photons', 'integralExt': 'photons', 'length':'length (pixels)', 'width':'width (pixels)', 'nhits': 'active pixels', 'slimness': 'width/length', 'density': 'photons/pixel', 'cmos_integral': 'CMOS integral (photons)', 'cmos_mean': 'CMOS mean (photons)', 'cmos_rms': 'CMOS RMS (photons)', 'tgausssigma': '#sigma_{transverse} (pixels)'}

    titles2d = {'integralvslength': ['length (pixels)','photons'], 'densityvslength' : ['length (pixels)','density (ph/pix)'],
                'densityvslength_zoom' : ['length (pixels)','density (ph/pix)'] }
    
    ## background histograms
    ret2 = {}
    for (region,var),h in ret.items():
        if ret[(region,var)].InheritsFrom('TH2'):
            ret[(region,var)].GetXaxis().SetTitle(titles2d[var][0])
            ret[(region,var)].GetYaxis().SetTitle(titles2d[var][1])
        elif ret[(region,var)].InheritsFrom('TH1'):
            ret[(region,var)].GetXaxis().SetTitle(titles[var])
            ret[(region,var)].GetXaxis().SetTitleSize(0.1)
        ret2[('cosm',var)] = h.Clone('cosm_{name}'.format(name=var))
        ret2[('fe',var)]   = h.Clone('fe_{name}'.format(name=var))
        if ret[(region,var)].InheritsFrom('TH1'):
            ret[(region,var)].Sumw2()
            ret[(region,var)].SetDirectory(0)
            ret2[('cosm',var)].SetDirectory(0)
            ret2[('fe',var)].SetDirectory(0)
        else:
            ret[(region,var)].SetName(region+var)
            ret2[('cosm',var)].SetName('cosm'+var)
            ret2[('fe',var)].SetName('fe'+var)

    ret.update(ret2)

    ## now fill the histograms 
    selected = 0
    for runtype in ['fe','ambe','cosm']:
        for ie,event in enumerate(tfiles[runtype].Events):
            for cmosvar in ['cmos_integral','cmos_mean','cmos_rms']:
                ret[runtype,cmosvar].Fill(getattr(event,cmosvar))
            for isc in range(getattr(event,"nSc" if cluster=='sc' else 'nCl')):
                #if getattr(event,"{clutype}_iteration".format(clutype=cluster))[isc]!=2:
                #    continue
                nhits = getattr(event,"{clutype}_nhits".format(clutype=cluster))[isc]
                density = getattr(event,"{clutype}_integral".format(clutype=cluster))[isc]/nhits if nhits>0 else 0
                xmin = getattr(event,"{clutype}_xmin".format(clutype=cluster))[isc]
                xmax = getattr(event,"{clutype}_xmax".format(clutype=cluster))[isc]
                ymin = getattr(event,"{clutype}_ymin".format(clutype=cluster))[isc]
                ymax = getattr(event,"{clutype}_ymax".format(clutype=cluster))[isc]
                xmean = getattr(event,"{clutype}_xmean".format(clutype=cluster))[isc]
                ymean = getattr(event,"{clutype}_ymean".format(clutype=cluster))[isc]
                length =  getattr(event,"{clutype}_length".format(clutype=cluster))[isc]
                photons = getattr(event,"{clutype}_integral".format(clutype=cluster))[isc]
                integral =  getattr(event,"{clutype}_integral".format(clutype=cluster))[isc]
                slimness = getattr(event,"{clutype}_width".format(clutype=cluster))[isc] / getattr(event,"{clutype}_length".format(clutype=cluster))[isc]
                # gainCalibnInt = integral*1.1 if runtype=='ambe' else integral 
                gainCalibnInt = integral
                # if not (30e3 < gainCalibnInt < 40e+3):
                #     continue
                if length > 1000:
                    continue
                if slimness < 0.3:
                    continue
                if density < 5:
                    continue
                #if length>50:
                #    continue
                #if photons < 1000:
                #    continue
                #if not withinFCFull(xmin,ymin,xmax,ymax):
                if not withinFC(xmean,ymean):
                    continue
                #if not slimnessCut(getattr(event,"{clutype}_length".format(clutype=cluster))[isc],getattr(event,"{clutype}_width".format(clutype=cluster))[isc]):
                 #   continue
                #if not integralCut(getattr(event,"{clutype}_integral".format(clutype=cluster))[isc]):
                #    continue
                for var in ['integral','length','width','nhits','tgausssigma']:
                    ret[(runtype,var)].Fill(getattr(event,("{clutype}_{name}".format(clutype=cluster,name=var)))[isc])
                ret[(runtype,'integralExt')].Fill(getattr(event,"{clutype}_integral".format(clutype=cluster))[isc])
                
                ret[(runtype,'slimness')].Fill(getattr(event,"{clutype}_width".format(clutype=cluster))[isc] / getattr(event,"{clutype}_length".format(clutype=cluster))[isc])
                ret[(runtype,'density')].Fill(density)
                #sigma =  getattr(event,"{clutype}_tgausssigma".format(clutype=cluster))[isc] * 0.125 * 6 # use 2*3 sigma to contain 99.7% of prob.
                #length =  getattr(event,"{clutype}_lgausssigma".format(clutype=cluster))[isc] * 0.125 * 6 - sigma # subtract the sigma to remove the diffusion
                sigma =  getattr(event,"{clutype}_width".format(clutype=cluster))[isc] * 0.125 * 6 # use 2*3 sigma to contain 99.7% of prob.
                length_sub = math.sqrt(max(0,length*length - sigma*sigma))
                ret[(runtype,'integralvslength')].Fill(length,integral)

                ret[(runtype,'densityvslength')]     .Fill(length,density)
                ret[(runtype,'densityvslength_zoom')].Fill(length,density)
                # ret[(runtype,'integralvslength')].SetPoint(selected,length_sub,integral) 
                # ret[(runtype,'sigmavslength')].SetPoint(selected,length_sub,sigma)
                # ret[(runtype,'sigmavsintegral')].SetPoint(selected,integral,sigma)
                selected += 1

                ### for debugging purposes:
                # if 30e3 < integral < 40e+3 and event.run==2156:
                #     print("population1 density = {d:.1f}\t{r}\t{e}\t{y}\t{x}\t{phot}".format(d=density,r=event.run,e=event.event,y=int(event.sc_ymean[isc]/4.),x=int(event.sc_xmean[isc]/4.),phot=int(event.sc_integral[isc])))

                
    return ret,entries

def getCanvas():
    c = ROOT.TCanvas('c','',1200,1200)
    lMargin = 0.14
    rMargin = 0.10
    bMargin = 0.15
    tMargin = 0.10
    c.SetLeftMargin(lMargin)
    c.SetRightMargin(rMargin)
    c.SetTopMargin(tMargin)
    c.SetBottomMargin(bMargin)
    c.SetFrameBorderMode(0);
    c.SetBorderMode(0);
    c.SetBorderSize(0);
    return c

def drawOneGraph(graph,var,plotdir):
    ROOT.gStyle.SetOptStat(0)
    c = ROOT.TCanvas('c','',1200,1200)
    lMargin = 0.12
    rMargin = 0.05
    bMargin = 0.30
    tMargin = 0.07

    graph.SetMarkerStyle(ROOT.kOpenCircle)
    graph.SetMarkerColor(1)
    graph.SetMarkerSize(1)
    graph.Draw('AP')

    xtitle = var.split('vs')[1]
    ytitle = var.split('vs')[0]

    if 'length' in xtitle:
        graph.GetXaxis().SetRangeUser(-6,15)
    if 'integral' in ytitle:
        graph.GetYaxis().SetRangeUser(0,100)
    if 'integral' in xtitle:
        graph.GetXaxis().SetRangeUser(0,100)
        
    titles = [xtitle,ytitle]
    for i,t in enumerate(titles):
        if 'integral' in t:  titles[i] = 'energy [keV]'
        if 'sigma' in t: titles[i] = 'transverse width (6#sigma) [mm]'
        if 'length' in t: titles[i] = 'length (diffusion subtracted) [mm]'

    graph.GetXaxis().SetTitle(titles[0])
    graph.GetYaxis().SetTitle(titles[1])

    for ext in ['png','pdf','root']:
        c.SaveAs("{plotdir}/graph_{var}.{ext}".format(plotdir=plotdir,var=var,ext=ext))

def drawOne(histo_sig,histo_bkg,histo_sig2=None,plotdir='./',normEntries=False):
    ROOT.gStyle.SetOptStat(0)
    
    c = ROOT.TCanvas('c','',1200,1200)
    lMargin = 0.12
    rMargin = 0.05
    bMargin = 0.30
    tMargin = 0.07
    padTop = ROOT.TPad('padTop','',0.,0.4,1,0.98)
    padTop.SetLeftMargin(lMargin)
    padTop.SetRightMargin(rMargin)
    padTop.SetTopMargin(tMargin)
    padTop.SetBottomMargin(0)
    padTop.SetFrameBorderMode(0);
    padTop.SetBorderMode(0);
    padTop.SetBorderSize(0);
    padTop.Draw()

    padBottom = ROOT.TPad('padBottom','',0.,0.02,1,0.4)
    padBottom.SetLeftMargin(lMargin)
    padBottom.SetRightMargin(rMargin)
    padBottom.SetTopMargin(0)
    padBottom.SetBottomMargin(bMargin)
    padBottom.SetFrameBorderMode(0);
    padBottom.SetBorderMode(0);
    padBottom.SetBorderSize(0);
    padBottom.Draw()

    padTop.cd()
    ymax = max(histo_bkg.GetMaximum(),histo_sig.GetMaximum())
    if histo_sig2:
        ymax = max(histo_sig2.GetMaximum(),ymax)
    histo_sig.SetMaximum(1.2*ymax)
    if normEntries:
        histo_sig.GetYaxis().SetTitle('clusters (normalized to AmBe events)')
    else:
        histo_sig.GetYaxis().SetTitle('clusters (a.u.)')
    histo_sig.Draw("pe")
    histo_bkg.Draw("hist same")
    if histo_sig2:
        histo_sig2.Draw("hist same")
    #padTop.SetLogy(1)

    ## rescale the Fe bkg by the scale factor in the pure cosmics CR
    histo_bkg.Scale(cosm_rate_calib[0])
    
    histos = [histo_sig,histo_bkg,histo_sig2]
    labels = ['AmBe','%.2f #times no source' % cosm_rate_calib[0], '%.1f #times ^{55}Fe' % fe_integral_rescale]
    styles = ['pe','f','f']
    
    legend = doLegend(histos,labels,styles,corner="TR")
    legend.Draw()
    
    padBottom.cd()
    ratios = []; labelsR = []; stylesR = []
    ratio = histo_sig.Clone(histo_sig.GetName()+"_diff")
    ratio.SetMarkerStyle(ROOT.kFullDotLarge)
    ratio.SetMarkerColor(ROOT.kBlack)
    ratio.SetLineColor(ROOT.kBlack)
    ratio.Sumw2()
    ratio.Add(histo_bkg,-1.0)
    ratio.GetYaxis().SetTitleSize(0.05)
    ratio.GetYaxis().SetTitle("source - nosource")
    ratio.GetYaxis().CenterTitle()
    ratio.Draw('pe')
    ratios.append(ratio)
    labelsR.append('AmBe - no source')
    stylesR.append('pe')
    
    if histo_sig2:
        ratio2 = histo_sig2.Clone(histo_sig.GetName()+"fe_diff")
        ratio2.SetMarkerStyle(ROOT.kFullDotLarge)
        ratio2.SetMarkerColor(ROOT.kRed+2)
        ratio2.SetLineColor(ROOT.kRed+2)
        ratio2.Sumw2()
        ratio2.Add(histo_bkg,-1.0)
        ratio2.GetYaxis().SetTitleSize(0.05)
        ratio2.GetYaxis().SetTitle("{num} - {den}".format(num=labels[0],den=labels[1]))
        ratio2.Draw('pe same')
        ratios.append(ratio2)
        labelsR.append('%.1f #times ^{55}Fe - no source' % fe_integral_rescale)
        stylesR.append('pe')
        rmax = max(ratio.GetMaximum(),ratio2.GetMaximum())
        ratio.SetMaximum(rmax)
        
    legendR = doLegend(ratios,labelsR,stylesR,corner="TR")
    legendR.Draw()

    line = ROOT.TLine()
    line.DrawLine(ratio.GetXaxis().GetBinLowEdge(1), 0, ratio.GetXaxis().GetBinLowEdge(ratio.GetNbinsX()+1), 0)
    line.SetLineStyle(3)
    line.SetLineColor(ROOT.kBlack)
    
    for ext in ['png','pdf']:
        c.SaveAs("{plotdir}/{var}.{ext}".format(plotdir=plotdir,var=histo_sig.GetName(),ext=ext))

    of = ROOT.TFile.Open("{plotdir}/{var}.root".format(plotdir=plotdir,var=histo_sig.GetName()),'recreate')
    histo_bkg.Write()
    histo_sig.Write()
    ratio.Write()
    if histo_sig2:
        histo_sig2.Write()
        ratio2.Write()
    of.Close()

## this just plots 2D in the dumbest way
def drawOne2D_raw(histo_sig,histo_bkg1,histo_bkg2,plotdir='./'):
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetPalette(ROOT.kRainBow)
    
    ROOT.gStyle.SetNumberContours(51)
    ROOT.gErrorIgnoreLevel = 100
    
    c = ROOT.TCanvas('c','',3600,1200)
    c.Divide(3,1)

    c.cd(1)
    histo_sig.SetTitle('AmBe')
    histo_sig.Draw('colz')
    
    c.cd(2)
    histo_bkg1.SetTitle('^{55}Fe')
    histo_bkg1.Draw("colz")

    c.cd(3)
    histo_bkg2.SetTitle('no source')
    histo_bkg2.Draw("colz")

    
    for ext in ['png','pdf']:
        c.SaveAs("{plotdir}/{var}_3species.{ext}".format(plotdir=plotdir,var=histo_sig.GetName(),ext=ext))

    of = ROOT.TFile.Open("{plotdir}/{var}_3species.root".format(plotdir=plotdir,var=histo_sig.GetName()),'recreate')
    histo_bkg2.Write()
    histo_bkg1.Write()
    histo_sig.Write()
    of.Close()
    

## the following does background subtraction with a second histogram
def drawOne2D(histo_sig,histo_bkg,plotdir='./',normEntries=False):
    ROOT.gStyle.SetOptStat(0)

    ROOT.TColor.CreateGradientColorTable(3,
                                      array ("d", [0.00, 0.50, 1.00]),
                                      ##array ("d", [1.00, 1.00, 0.00]),
                                      ##array ("d", [0.70, 1.00, 0.34]),
                                      ##array ("d", [0.00, 1.00, 0.82]),
                                      array ("d", [0.00, 1.00, 1.00]),
                                      array ("d", [0.34, 1.00, 0.65]),
                                      array ("d", [0.82, 1.00, 0.00]),
                                      255,  0.95)

    ROOT.gStyle.SetNumberContours(51)
    ROOT.gErrorIgnoreLevel = 100
    
    c = ROOT.TCanvas('c','',3600,1200)
    c.Divide(3,1)

    c.cd(1)
    histo_sig.SetTitle('AmBe')
    histo_sig.Draw('colz')
    
    c.cd(2)
    histo_bkg.SetTitle('no source')
    histo_bkg.Draw("colz")

    c.cd(3)
    ratio = histo_sig.Clone(histo_sig.GetName()+"_diff")
    ratio.SetTitle('AmBe - NoSource')
    ratio.Sumw2()
    ratio.Add(histo_bkg,-1*cosm_rate_calib[0])
    ratio.GetYaxis().SetTitleSize(0.05)
    ratio.GetYaxis().SetTitle("left - right")
    ratio.Draw('colz')
    
    maxY = max(ratio.GetMaximum(),abs(ratio.GetMinimum()))
    ratio.SetMaximum( 0.5 * maxY)
    ratio.SetMinimum(-0.5 * maxY)
    
    for ext in ['png','pdf']:
        c.SaveAs("{plotdir}/{var}.{ext}".format(plotdir=plotdir,var=histo_sig.GetName(),ext=ext))

    of = ROOT.TFile.Open("{plotdir}/{var}.root".format(plotdir=plotdir,var=histo_sig.GetName()),'recreate')
    histo_bkg.Write()
    histo_sig.Write()
    of.Close()

def drawSpectra(histos,plotdir,entries,normEntries=False):
    variables = [var for (reg,var) in list(histos.keys()) if reg=='fe']

    ROOT.gStyle.SetHatchesSpacing(0.3)
    ROOT.gStyle.SetHatchesLineWidth(1)

    for var in variables:
        if histos[('ambe',var)].InheritsFrom('TH1'):
            if normEntries:
                histos[('fe',var)].Scale(float(entries['ambe'])/float(entries['fe'])*fe_integral_rescale)
                histos[('cosm',var)].Scale(float(entries['ambe'])/float(entries['cosm']))
            else:
                histos[('ambe',var)].Scale(1./histos[('ambe',var)].Integral())
                histos[('cosm',var)].Scale(1./histos[('cosm',var)].Integral())
                histos[('fe',var)].Scale(1./histos[('fe',var)].Integral())
        if histos[('ambe',var)].InheritsFrom('TH2'):
            if var in ['integralvslength','densityvslength_zoom']:
                drawOne2D(histos[('ambe',var)],histos[('fe',var)],plotdir)
            drawOne2D_raw(histos[('ambe',var)],histos[('fe',var)],histos[('cosm',var)],plotdir)
        elif histos[('ambe',var)].InheritsFrom('TH1'):
            histos[('ambe',var)].SetMarkerStyle(ROOT.kFullDotLarge)
            histos[('ambe',var)].SetLineColor(ROOT.kBlack)
            histos[('cosm',var)].SetFillColor(ROOT.kAzure+6)
            histos[('cosm',var)].SetFillStyle(3345)
            if histos[('fe',var)]:
                histos[('fe',var)].SetFillColor(ROOT.kRed+6)
                histos[('fe',var)].SetFillStyle(3354)
            drawOne(histos[('ambe',var)],histos[('cosm',var)],histos[('fe',var)],plotdir,normEntries)
        elif histos[('fe',var)].InheritsFrom('TGraph'):
            drawOneGraph(histos[('ambe',var)],var,plotdir)
            
def plotEnergyVsDistance(plotdir):

    tf_fe55 = ROOT.TFile('runs/reco_run01740_3D.root')
    tree = tf_fe55.Get('Events')

    np = 9 # number of points
    dist = 100 # distance from center in pixels
    x = [dist*i for i in range(np+1)]
    y_mean = []; y_res = []

    cut_base = 'cl_iteration==2'
    integral = ROOT.TH1F('integral','',100,600,3000)
    
    for p in range(np):
        cut = "{base} && TMath::Hypot(cl_xmean-1024,cl_ymean-1024)>{r_min} && TMath::Hypot(cl_xmean-1024,cl_ymean-1024)<{r_max}".format(base=cut_base,r_min=x[p],r_max=x[p+1])
        tree.Draw('cl_integral>>integral',cut)
        mean = integral.GetMean()
        rms  = integral.GetRMS()
        y_mean.append(mean)
        y_res.append(rms/mean)
        integral.Reset()

    gr_mean = ROOT.TGraph(np,array('f',x),array('f',y_mean))
    gr_res = ROOT.TGraph(np,array('f',x),array('f',y_res))
    gr_mean.SetMarkerStyle(ROOT.kOpenCircle)
    gr_res.SetMarkerStyle(ROOT.kOpenCircle)
    gr_mean.SetMarkerSize(2)
    gr_res.SetMarkerSize(2)
    
    gr_mean.SetTitle('')
    gr_res.SetTitle('')
    
    c = ROOT.TCanvas('c','',1200,1200)
    lMargin = 0.12
    rMargin = 0.05
    bMargin = 0.30
    tMargin = 0.07

    gr_mean.Draw('AP')
    gr_mean.GetXaxis().SetTitle('distance from center (pixels)')
    gr_mean.GetYaxis().SetTitle('integral (photons)')

    for ext in ['png','pdf']:
        c.SaveAs("{plotdir}/mean.{ext}".format(plotdir=plotdir,ext=ext))

    gr_res.Draw('AP')
    gr_res.GetXaxis().SetTitle('distance from center (pixels)')
    gr_res.GetYaxis().SetTitle('resolution (rms)')
    gr_res.GetYaxis().SetRangeUser(0.10,0.50)

    for ext in ['png','pdf']:
        c.SaveAs("{plotdir}/rms.{ext}".format(plotdir=plotdir,ext=ext))

    print(x)
    print(y_mean)
    print(y_res)

def plotCameraEnergyVsPosition(plotdir,var='integral'):
    
    x = []
    y_mean = []; y_res = []
    
    for i in range(0,6):
        
        mean, rms, i, leg = plotHistFit(plotdir,var,i)
        x.append(i)
        y_mean.append(mean)
        y_res.append(rms/mean)

    print(y_res)
    np = len(x)
    
    gr_mean = ROOT.TGraph(np,array('f',x),array('f',y_mean))
    gr_res = ROOT.TGraph(np,array('f',x),array('f',y_res))
    gr_mean.GetXaxis().SetRangeUser(0,21)
    gr_res.GetXaxis().SetRangeUser(0,21)
    gr_mean.GetYaxis().SetRangeUser(0,max(y_mean)*1.2)
    gr_res. GetYaxis().SetRangeUser(0,max(y_res)*1.2)
    gr_mean.SetMarkerStyle(ROOT.kOpenCircle)
    gr_res.SetMarkerStyle(ROOT.kOpenCircle)
    gr_mean.SetMarkerSize(2)
    gr_res.SetMarkerSize(2)
    
    gr_mean.SetTitle('')
    gr_res.SetTitle('')

    c = ROOT.TCanvas('c','',1200,1200)
    lMargin = 0.17
    rMargin = 0.05
    bMargin = 0.15
    tMargin = 0.07
    c.SetLeftMargin(lMargin)
    c.SetRightMargin(rMargin)
    c.SetTopMargin(tMargin)
    c.SetBottomMargin(bMargin)
    c.SetFrameBorderMode(0);
    c.SetBorderMode(0);
    c.SetBorderSize(0);
    c.SetGrid();

    gr_mean.Draw('AP')
    gr_mean.GetXaxis().SetTitle('Source Position [cm]')
    gr_mean.GetYaxis().SetTitle('{leg}'.format(leg=leg))

    for ext in ['png','pdf']:
        c.SaveAs("{plotdir}/CameraMean_{var}_60-40.{ext}".format(plotdir=plotdir,var=var,ext=ext))

    gr_res.Draw('AP')
    gr_res.GetXaxis().SetTitle('Source Position [cm]')
    gr_res.GetYaxis().SetTitle('Resolution [rms]')

    for ext in ['png','pdf']:
        c.SaveAs("{plotdir}/CameraRMS_{var}_60-40.{ext}".format(plotdir=plotdir,var=var,ext=ext))
    
    
def plotPMTEnergyVsPosition(plotdir):
    tf_fe55 = ROOT.TFile('runs/reco_run01754_to_run01759.root')
    tree = tf_fe55.Get('Events')

    runs = list(range(1754,1760))
    integral = ROOT.TH1F('integral','',100,2000,20000)

    np = len(runs)
    x = []
    y_mean = []; y_res = []
    
    for i,r in enumerate(runs):
        cut = 'run=={r} && pmt_tot<100'.format(r=r)
        tree.Draw('pmt_integral>>integral',cut)
        mean = integral.GetMean()
        rms  = integral.GetRMS()
        x.append(i)
        y_mean.append(mean)
        y_res.append(rms/mean)
        integral.Reset()


    print(y_res)
    
    gr_mean = ROOT.TGraph(np,array('f',x),array('f',y_mean))
    gr_res = ROOT.TGraph(np,array('f',x),array('f',y_res))
    gr_mean.GetXaxis().SetRangeUser(-1,np)
    gr_res.GetXaxis().SetRangeUser(-1,np)
    gr_mean.GetYaxis().SetRangeUser(5000,9000)
    gr_res. GetYaxis().SetRangeUser(0,1.0)
    gr_mean.SetMarkerStyle(ROOT.kOpenCircle)
    gr_res.SetMarkerStyle(ROOT.kOpenCircle)
    gr_mean.SetMarkerSize(2)
    gr_res.SetMarkerSize(2)
    
    gr_mean.SetTitle('')
    gr_res.SetTitle('')

    c = ROOT.TCanvas('c','',1200,1200)
    lMargin = 0.17
    rMargin = 0.05
    bMargin = 0.15
    tMargin = 0.07
    c.SetLeftMargin(lMargin)
    c.SetRightMargin(rMargin)
    c.SetTopMargin(tMargin)
    c.SetBottomMargin(bMargin)
    c.SetFrameBorderMode(0);
    c.SetBorderMode(0);
    c.SetBorderSize(0);
    

    gr_mean.Draw('AP')
    gr_mean.GetXaxis().SetTitle('source position index')
    gr_mean.GetYaxis().SetTitle('PMT integral (mV)')

    for ext in ['png','pdf']:
        c.SaveAs("{plotdir}/mean.{ext}".format(plotdir=plotdir,ext=ext))

    gr_res.Draw('AP')
    gr_res.GetXaxis().SetTitle('source position index')
    gr_res.GetYaxis().SetTitle('resolution (rms)')

    for ext in ['png','pdf']:
        c.SaveAs("{plotdir}/rms.{ext}".format(plotdir=plotdir,ext=ext))

    print(x)
    print(y_mean)
    print(y_res)


def plotCameraPMTCorr(outdir):
    tf_fe55 = ROOT.TFile('runs/reco_run01754_to_run01759.root')
    tree = tf_fe55.Get('Events')

    tot_vs_nhits = ROOT.TH2F('nhits_vs_tot','',45,20,100,30,100,400)
    tot_vs_nhits.GetXaxis().SetTitle("T.o.T. (ms)")
    tot_vs_nhits.GetYaxis().SetTitle("supercluster pixels")
    tot_vs_nhits.SetContour(100)
    
    ## fill the 2D histogram
    for event in tree:
        if event.pmt_tot > 100: continue
        for isc in range(event.nSc):
            if event.sc_iteration[isc]!=2: continue
            if event.sc_width[isc]/event.sc_length[isc]<0.7: continue
            if not withinFC(event.sc_xmean[isc],event.sc_ymean[isc],700,700): continue
            tot_vs_nhits.Fill(event.pmt_tot,event.sc_nhits[isc])

    ## profile for better understanding
    profX = tot_vs_nhits.ProfileX()
    profX.SetMarkerStyle(ROOT.kFullCircle)
    profX.SetLineColor(ROOT.kBlack)
    profX.SetMarkerColor(ROOT.kBlack)
    profX.GetYaxis().SetRangeUser(180,310)
    profX.GetYaxis().SetTitle("average pixels in SC")

    ROOT.gStyle.SetPalette(ROOT.kRainBow)
    ROOT.gStyle.SetOptStat(0)
    c = getCanvas()
    tot_vs_nhits.Draw("colz")
    for ext in ['png','pdf','root']:
        c.SaveAs('{plotdir}/{name}.{ext}'.format(plotdir=outdir,name=tot_vs_nhits.GetName(),ext=ext))

    profX.Draw('pe1')
    for ext in ['png','pdf','root']:
        c.SaveAs('{plotdir}/{name}_profX.{ext}'.format(plotdir=outdir,name=tot_vs_nhits.GetName(),ext=ext))
        
def plotHistFit(plotdir,var='integral',i=0):
    import numpy as np
    
    ROOT.gStyle.SetOptFit(1011)
    gas=60
    if gas == 70:
        pos  = [0, 1, 2, 3, 4, 5, 6]
        run  = [2274, 2275, 2276, 2277, 2278, 2279, 2280]
        dist = (23-np.array([19.5, 16.5, 14.3, 12.5, 10.5, 8.2, 6.2])).tolist()
    else:
        pos  = [0, 1, 2, 3, 4, 5]
        run  = [2160, 2161, 2162, 2163, 2164, 2165]
        dist = (23-np.array([19.5, 16.5, 14.3, 12.5, 10.5, 8.2])).tolist()
        
    
    if var == 'integral':
        var1 = 'cl_integral'
        leg = 'Integral [ph]'
        histlimit = 6000
    elif var == 'length':
        var1 = 'cl_length*125E-3'
        leg = 'Length [mm]'
        if gas == 70:
            histlimit = 12
        else:
            histlimit = 7
    elif var == 'width':
        var1 = 'cl_width*125E-3'
        leg = 'Width [mm]'
        histlimit = 10
    elif var == 'size':
        var1 = 'cl_size'
        leg = 'Size [px]'
        histlimit = 1600
    elif var == 'slimness':
        var1 = 'cl_width/cl_length'
        leg = 'Slimness [w/l]'
        histlimit = 1.2
    else:
        exit()
    
    if gas == 70:
        tf_fe55 = ROOT.TFile('../reco_run02274_to_run02280.root')    
    else:
        tf_fe55 = ROOT.TFile('../reco_run02160_to_run02165.root')
        
    tree = tf_fe55.Get('Events')
    
    c = ROOT.TCanvas('','',800,600)

    hist = ROOT.TH1F('hist','%.2f cm between Source and GEM' % (dist[i]),100,0,histlimit)
    hist.Sumw2()

    cut_base = 'cl_iteration==2 && run=={r}'.format(r=run[i])
    cut = "{base} && TMath::Hypot(cl_xmean-1024,(cl_ymean-1024)*1.2)<{r_max}".format(base=cut_base,r_max=400)

    tree.Draw("{var}>>hist".format(var=var1),cut)
    hist.SetFillStyle(3005)
    mean = hist.GetMean()
    rms  = hist.GetRMS()
    
    # add Polya Fuction
    func='gauss'
    
    if func == 'gauss':
        print("Using Gauss fit")
        f = ROOT.TF1('f','gaus')
        f.SetParameter(1,mean);
        f.SetParLimits(1,mean-3*rms,mean+3*rms);
        f.SetParameter(2,rms);
        #f.SetParLimits(2,300,600);
        fitRe = hist.Fit(f,'S')
        rMean  = f.GetParameter(1)
        rSigma = f.GetParameter(2)
    else:
        print("Using Polya fit needs to be fixed")
             
        #[0] = b
        #[1] = nt
        #[2] = k
        #k = 1/[0] -1
        #[x] = n

        pol_A = "(1/[0]*[1])"
        pol_B = "(1/TMath::Factorial(1/([0] -1)))"
        pol_C = "TMath::Power(x/([0]*[1]), (1/([0] -1)))"
        pol_D = "exp((-1*x)/([0]*[1]))"
        pol = "(%s)*(%s)*(%s)*(%s)" % (pol_A , pol_B , pol_C, pol_D)
        
        polyaFit = ROOT.TF1("polyafit", pol, 0, 6000)
        #polyaFit.SetParameter (0, 500)
        polyaFit.SetParameter (1, 2600)
        
        hist.Fit(polyaFit ,"S")
        rMean  = polyaFit.GetParameter(0)
        rSigma = polyaFit.GetParameter(1)
        
    hist.Draw('hist sames')  
    
    ROOT.gPad.Update()
    #h.GetXaxis().SetRangeUser(0,0.25)
    hist.GetYaxis().SetTitle('Counts')
    hist.GetXaxis().SetTitle('{leg}'.format(leg=leg))
    #'Position %d' % (pos[i])
    c.SetGrid()
    c.Draw()
    c.SaveAs("{plotdir}/hist_{var}_pos{pos}_60-40.pdf".format(plotdir=plotdir,var=var,pos=pos[i]))
    hist.Reset()
    
    return rMean,rSigma,dist[i],leg

def plotHist2D(plotdir,v1='integral',v2='slimness',i=0):
    import numpy as np
    
    ROOT.gStyle.SetOptFit(1011)
    
    gas=70
    #i=5
    
    if gas == 70:
        pos  = [0, 1, 2, 3, 4, 5, 6]
        run  = [2274, 2275, 2276, 2277, 2278, 2279, 2280]
        dist = (23-np.array([19.5, 16.5, 14.3, 12.5, 10.5, 8.2, 6.2])).tolist()
        gg   = '70-30'
    else:
        pos  = [0, 1, 2, 3, 4, 5]
        run  = [2160, 2161, 2162, 2163, 2164, 2165]
        dist = (23-np.array([19.5, 16.5, 14.3, 12.5, 10.5, 8.2])).tolist()
        gg   = '60-40'
        
    if gas == 70:
        tf_fe55 = ROOT.TFile('../reco_run02274_to_run02280.root')    
    else:
        tf_fe55 = ROOT.TFile('../reco_run02160_to_run02165.root')        
    
    vr1,legy,histlimity = varChoice(v1)
    vr2,legx,histlimitx = varChoice(v2)
        
    var1 = vr1+":"+vr2
        
    tree = tf_fe55.Get('Events')
    
    c = ROOT.TCanvas('','',800,800)

    hist = ROOT.TH2F('hist2D','%.2f cm between Source and GEM' % (dist[i]),1000,0,histlimity,1000,0,histlimitx)
    hist.Sumw2()

    cut_base = 'cl_iteration==2 && run=={r}'.format(r=run[i])
    cut = "{base} && TMath::Hypot(cl_xmean-1024,(cl_ymean-1024)*1.2)<{r_max}".format(base=cut_base,r_max=400)

    tree.Draw("{var}>>hist".format(var=var1),cut)
    hist.SetFillStyle(3005)
    
    ROOT.gPad.Update()
    #h.GetXaxis().SetRangeUser(0,0.25)
    hist.GetYaxis().SetTitle('{leg}'.format(leg=legy))
    hist.GetXaxis().SetTitle('{leg}'.format(leg=legx))
    c.SetGrid()
    c.Draw()
    c.SaveAs("{plotdir}/hist_{var}_vs_{var2}_pos{pos}_{gg}.pdf".format(plotdir=plotdir,var=v1,var2=v2,pos=pos[i],gg=gg))
    hist.Reset()


def getOneROC(sigh,bkgh,direction='gt'):
    
    ## this assumes the same binning, but it is always the case here
    plots = [sigh,bkgh]
    integrals = [p.Integral() for p in plots]
    nbins = sigh.GetNbinsX()

    efficiencies = []
    for ip,p in enumerate(plots):
        if direction=='gt':
            eff = [p.Integral(binx,nbins)/integrals[ip] for binx in range(0,nbins)]
        else:
            eff = [p.Integral(0,binx)/integrals[ip] for binx in range(0,nbins)]
        efficiencies.append(eff)

    ## graph for the roc
    roc = ROOT.TGraph(nbins)
    for i in range(nbins):
        roc.SetPoint(i, efficiencies[0][i], 1-efficiencies[1][i])
        print ("point {i}, S eff={seff:.2f}, B eff={beff:.3f}".format(i=i,seff=efficiencies[0][i],beff=efficiencies[1][i]))
    roc.SetTitle('')
        
    return roc

def drawROC(varname,odir):
    tf = ROOT.TFile.Open('{odir}/{var}.root'.format(odir=odir,var=varname))

    print ("===> Cosm roc")
    cosm_roc = getOneROC(tf.Get('{var}_diff'.format(var=varname)), tf.Get('cosm_{var}'.format(var=varname)))
    print ("===> Fe roc")
    fe_roc   = getOneROC(tf.Get('{var}_diff'.format(var=varname)), tf.Get('fe_{var}'.format(var=varname)))

    c = ROOT.TCanvas('c','',1200,1200)
    cosm_roc.SetMarkerStyle(ROOT.kFullDotLarge)
    cosm_roc.SetMarkerSize(2)
    cosm_roc.SetMarkerColor(ROOT.kBlack)
    cosm_roc.SetLineColor(ROOT.kBlack)

    fe_roc.SetMarkerStyle(ROOT.kFullSquare)
    fe_roc.SetMarkerSize(2)
    fe_roc.SetMarkerColor(ROOT.kRed)
    fe_roc.SetLineColor(ROOT.kRed)

    cosm_roc.Draw('APC')
    cosm_roc.GetXaxis().SetTitle('AmBe efficiency')
    cosm_roc.GetYaxis().SetTitle('Background rejection')
    fe_roc.Draw('PC')

    graphs = [cosm_roc,fe_roc]
    labels = ['no source bkg','^{55}Fe bkg']
    styles = ['pl','pl']
    legend = doLegend(graphs,labels,styles,corner="TR")
    
    for ext in ['png','pdf']:
        c.SaveAs("{plotdir}/{var}_roc.{ext}".format(plotdir=odir,var=varname,ext=ext))
             
    
if __name__ == "__main__":

    parser = optparse.OptionParser(usage='usage: %prog [opts] ', version='%prog 1.0')
    parser.add_option('', '--make'   , type='string'       , default='tworuns' , help='run simple plots (options = tworuns, evsdist, pmtvsz, cluvspmt, cluvsz, multiplicity, hist1d, hist2d)')
    parser.add_option('', '--outdir' , type='string'       , default='./'      , help='output directory with directory structure and plots')
    parser.add_option('', '--var' , type='string'       , default='integral'      , help='variable to plot the histogram')
    parser.add_option('', '--pos' , type='int'       , default=0      , help='position of the iron source')
    parser.add_option('', '--var2' , type='string'       , default='slimness'      , help='variable2 to plot the histogram 2D')
   
    (options, args) = parser.parse_args()

    ## make the output directory first
    os.system('mkdir -p {od}'.format(od=options.outdir))
    
    if options.make in ['all','multiplicity']:
        plotNClusters()

    if options.make in ['all','tworuns']:
        histograms,entries = fillSpectra()
        odir = options.outdir
        os.system('mkdir -p {od}'.format(od=odir))
        drawSpectra(histograms,odir,entries,normEntries=True)
        os.system('cp ../index.php {od}'.format(od=odir))
        drawROC('density',odir)
        
    if options.make in ['all','evsdist']:
        plotEnergyVsDistance(options.outdir)

    if options.make in ['all','pmtvsz']:
        plotPMTEnergyVsPosition(options.outdir)

    if options.make in ['all','cluvspmt']:
        plotCameraPMTCorr(options.outdir)
        
    if options.make in ['all','cluvsz']:
        plotCameraEnergyVsPosition(options.outdir, options.var)
    
    if options.make in ['all','hist1d']:        
        plotHistFit(options.outdir, options.var, options.pos)
        
    if options.make in ['all','hist2d']:
        plotHist2D(options.outdir, options.var, options.var2, options.pos)
