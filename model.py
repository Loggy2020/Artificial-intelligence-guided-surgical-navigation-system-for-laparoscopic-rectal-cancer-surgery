import torch
import torch.nn as nn
import torchvision.models as models


class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super(DoubleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )

    def forward(self, input):
        return self.conv(input)


class Unet(nn.Module):
    def __init__(self,in_ch,out_ch):
        super(Unet, self).__init__()

        self.conv1 = DoubleConv(in_ch, 64)
        self.pool1 = nn.MaxPool2d(2)
        self.conv2 = DoubleConv(64, 128)
        self.pool2 = nn.MaxPool2d(2)
        self.conv3 = DoubleConv(128, 256)
        self.pool3 = nn.MaxPool2d(2)
        self.conv4 = DoubleConv(256, 512)
        self.pool4 = nn.MaxPool2d(2)
        self.conv5 = DoubleConv(512, 1024)
        self.up6 = nn.ConvTranspose2d(1024, 512, 2, stride=2)
        self.conv6 = DoubleConv(1024, 512)
        self.up7 = nn.ConvTranspose2d(512, 256, 2, stride=2)
        self.conv7 = DoubleConv(512, 256)
        self.up8 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.conv8 = DoubleConv(256, 128)
        self.up9 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.conv9 = DoubleConv(128, 64)
        self.conv10 = nn.Conv2d(64, out_ch, 1)

    def forward(self, x):
        c1 = self.conv1(x)
        p1 = self.pool1(c1)
        c2 = self.conv2(p1)
        p2 = self.pool2(c2)
        c3 = self.conv3(p2)
        p3 = self.pool3(c3)
        c4 = self.conv4(p3)
        p4 = self.pool4(c4)
        c5 = self.conv5(p4)
        up_6 = self.up6(c5)
        merge6 = torch.cat([up_6, c4], dim=1)
        c6=self.conv6(merge6)
        up_7 = self.up7(c6)
        merge7 = torch.cat([up_7, c3], dim=1)
        c7 = self.conv7(merge7)
        up_8 = self.up8(c7)
        merge8 = torch.cat([up_8, c2], dim=1)
        c8 = self.conv8(merge8)
        up_9 = self.up9(c8)
        merge9 = torch.cat([up_9, c1], dim=1)
        c9 = self.conv9(merge9)
        c10 = self.conv10(c9)
        return c10


backbone = 'resnet50'
class DecoderBlock(nn.Module):
    """
    U-Net中的解码模块
    采用每个模块一个stride为1的3*3卷积加一个上采样层的形式
    上采样层可使用'deconv'、'pixelshuffle', 其中pixelshuffle必须要mid_channels=4*out_channles
    定稿采用pixelshuffle
    BN_enable控制是否存在BN，定稿设置为True
    """
    def __init__(self, in_channels, mid_channels, out_channels, upsample_mode='pixelshuffle', BN_enable=True):
        super().__init__()
        self.in_channels = in_channels
        self.mid_channels = mid_channels
        self.out_channels = out_channels
        self.upsample_mode = upsample_mode
        self.BN_enable = BN_enable

        self.conv = nn.Conv2d(in_channels=in_channels, out_channels=mid_channels, kernel_size=3, stride=1, padding=1, bias=False)

        if self.BN_enable:
            self.norm1 = nn.BatchNorm2d(mid_channels)
        self.relu1 = nn.ReLU(inplace=False)
        self.relu2 = nn.ReLU(inplace=False)

        if self.upsample_mode=='deconv':
            self.upsample = nn.ConvTranspose2d(in_channels=mid_channels, out_channels = out_channels,

                                                kernel_size=3, stride=2, padding=1, output_padding=1, bias=False)
        elif self.upsample_mode=='pixelshuffle':
            self.upsample = nn.PixelShuffle(upscale_factor=2)
        if self.BN_enable:
            self.norm2 = nn.BatchNorm2d(out_channels)

    def forward(self,x):
        x=self.conv(x)
        if self.BN_enable:
            x=self.norm1(x)
        x=self.relu1(x)
        x=self.upsample(x)
        if self.BN_enable:
            x=self.norm2(x)
        x=self.relu2(x)
        return x


class Resnet_Unet(nn.Module):
    def __init__(self, BN_enable=True, resnet_pretrain=False):
        super().__init__()
        self.BN_enable = BN_enable
        # encoder部分
        # 使用resnet34或50预定义模型，由于单通道入，因此自定义第一个conv层，同时去掉原fc层
        # 剩余网络各部分依次继承
        # 经过测试encoder取三层效果比四层更佳，因此降采样、升采样各取4次
        if backbone=='resnet34':
            resnet = models.resnet34(pretrained=resnet_pretrain)
            filters=[64,64,128,256,512]
        elif backbone=='resnet50':
            resnet = models.resnet50(pretrained=resnet_pretrain)
            filters=[64,256,512,1024,2048]
        self.firstconv = nn.Conv2d(in_channels=3, out_channels=64, kernel_size=7, stride=2, padding=3, bias=False)
        self.firstbn = resnet.bn1
        self.firstrelu = resnet.relu
        self.firstmaxpool = resnet.maxpool
        self.encoder1 = resnet.layer1
        self.encoder2 = resnet.layer2
        self.encoder3 = resnet.layer3

        # decoder部分
        self.center = DecoderBlock(in_channels=filters[3], mid_channels=filters[3]*4, out_channels=filters[3], BN_enable=self.BN_enable)
        self.decoder1 = DecoderBlock(in_channels=filters[3]+filters[2], mid_channels=filters[2]*4, out_channels=filters[2], BN_enable=self.BN_enable)
        self.decoder2 = DecoderBlock(in_channels=filters[2]+filters[1], mid_channels=filters[1]*4, out_channels=filters[1], BN_enable=self.BN_enable)
        self.decoder3 = DecoderBlock(in_channels=filters[1]+filters[0], mid_channels=filters[0]*4, out_channels=filters[0], BN_enable=self.BN_enable)
        if self.BN_enable:
            self.final = nn.Sequential(
                nn.Conv2d(in_channels=filters[0],out_channels=32, kernel_size=3, padding=1),
                nn.BatchNorm2d(32), 
                nn.ReLU(inplace=False),
                nn.Conv2d(in_channels=32, out_channels=1, kernel_size=1),
                nn.Sigmoid()
                )
        else:
            self.final = nn.Sequential(
                nn.Conv2d(in_channels=filters[0],out_channels=32, kernel_size=3, padding=1),
                nn.ReLU(inplace=False),
                nn.Conv2d(in_channels=32, out_channels=1, kernel_size=1), 
                nn.Sigmoid()
                )

    def forward(self,x):
        x = self.firstconv(x)
        x = self.firstbn(x)
        x = self.firstrelu(x)
        x_ = self.firstmaxpool(x)

        e1 = self.encoder1(x_)
        e2 = self.encoder2(e1)
        e3 = self.encoder3(e2)

        center = self.center(e3)

        d2 = self.decoder1(torch.cat([center,e2],dim=1))
        d3 = self.decoder2(torch.cat([d2,e1], dim=1))
        d4 = self.decoder3(torch.cat([d3,x], dim=1))

        return self.final(d4)
