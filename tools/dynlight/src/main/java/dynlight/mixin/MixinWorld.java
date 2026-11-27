package dynlight.mixin;

import com.llamalad7.mixinextras.injector.ModifyReturnValue;
import dynlight.LightSources;
import net.minecraft.util.math.BlockPos;
import net.minecraft.world.World;
import org.spongepowered.asm.mixin.Final;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Shadow;
import org.spongepowered.asm.mixin.injection.At;

/** Entities, tile entity renderers, particles and the first-person hand read light through this method. */
@Mixin(World.class)
public abstract class MixinWorld {

    @Shadow @Final public boolean isRemote;

    @ModifyReturnValue(method = "getCombinedLight", at = @At("RETURN"))
    private int dynlight$addDynamicLight(int packed, BlockPos pos) {
        return this.isRemote ? LightSources.apply(packed, pos) : packed;
    }
}
